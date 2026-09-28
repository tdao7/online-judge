import concurrent.futures
import json
import os
import subprocess
import sys
import threading
import time

# Ensure project root in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django import db
from django.db import connection
from judge.judgeapi import judge_submission
from judge.models import Judge, Language, Problem, Profile, Submission, SubmissionSource, SubmissionTestCase

TEST_CASES = [
    # Language, Expected Result, Expected Status, Name, Code
    ("PY3", "AC", "D", "PY3_AC", """
import sys
raw = sys.stdin.read().split()
if raw:
    n = int(raw[0])
    idx = 1
    for _ in range(n):
        print(int(raw[idx]) + int(raw[idx+1]))
        idx += 2
"""),
    ("PY3", "WA", "D", "PY3_WA", """
import sys
raw = sys.stdin.read().split()
if raw:
    n = int(raw[0])
    for _ in range(n):
        print(0)
"""),
    ("PY3", "TLE", "D", "PY3_TLE", """
while True:
    pass
"""),
    ("PY3", "CE", "CE", "PY3_CE", """
def invalid_syntax_py(
"""),
    ("CPP20", "AC", "D", "CPP20_AC", """
#include <iostream>
using namespace std;
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n;
    if (cin >> n) {
        while (n--) {
            long long a, b;
            cin >> a >> b;
            cout << (a + b) << "\\n";
        }
    }
    return 0;
}
"""),
    ("CPP20", "WA", "D", "CPP20_WA", """
#include <iostream>
using namespace std;
int main() {
    int n;
    if (cin >> n) {
        while (n--) {
            cout << 0 << "\\n";
        }
    }
    return 0;
}
"""),
    ("CPP20", "TLE", "D", "CPP20_TLE", """
#include <iostream>
int main() {
    volatile long long counter = 0;
    while (true) counter++;
    return 0;
}
"""),
    ("CPP20", "CE", "CE", "CPP20_CE", """
#include <iostream>
int main() {
    NON_EXISTENT_VARIABLE_ERR = 42;
    return 0;
}
"""),
    ("JAVA8", "AC", "D", "JAVA8_AC", """
import java.io.*;
public class aplusb {
    public static void main(String[] args) throws IOException {
        BufferedReader cin = new BufferedReader(new InputStreamReader(System.in));
        String line = cin.readLine();
        if (line == null) return;
        int n = Integer.parseInt(line.trim());
        for (int i = 0; i < n; i++) {
            String[] parts = cin.readLine().trim().split("\\\\s+");
            System.out.println(Integer.parseInt(parts[0]) + Integer.parseInt(parts[1]));
        }
    }
}
"""),
    ("JAVA8", "WA", "D", "JAVA8_WA", """
import java.io.*;
public class aplusb {
    public static void main(String[] args) throws IOException {
        BufferedReader cin = new BufferedReader(new InputStreamReader(System.in));
        String line = cin.readLine();
        if (line == null) return;
        int n = Integer.parseInt(line.trim());
        for (int i = 0; i < n; i++) {
            System.out.println(0);
        }
    }
}
"""),
    ("JAVA8", "TLE", "D", "JAVA8_TLE", """
public class aplusb {
    public static void main(String[] args) {
        long c = 0;
        while (true) c++;
    }
}
"""),
    ("JAVA8", "CE", "CE", "JAVA8_CE", """
public class aplusb {
    public static void main(String[] args) {
        int x = ;
    }
}
"""),
]

def get_bridge_pid():
    pid_file = os.path.join(BASE_DIR, 'runbridged.pid')
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
        except Exception:
            pass
    return None

def check_process_metrics(bridge_pid):
    metrics = {}
    if bridge_pid:
        try:
            res = subprocess.run(['ps', '-o', 'pid,rss,%cpu,command', '-p', str(bridge_pid)],
                                 capture_output=True, text=True)
            metrics['bridge_ps'] = res.stdout.strip()
        except Exception as e:
            metrics['bridge_ps'] = str(e)
        try:
            res = subprocess.run(f'lsof -p {bridge_pid} | wc -l', shell=True,
                                 capture_output=True, text=True)
            metrics['bridge_open_fds'] = int(res.stdout.strip())
        except Exception as e:
            metrics['bridge_open_fds'] = str(e)

    try:
        res = subprocess.run(['docker', 'top', 'dmoj-judge-runner'],
                             capture_output=True, text=True)
        metrics['docker_top'] = res.stdout.strip()
    except Exception as e:
        metrics['docker_top'] = str(e)

    return metrics

def run_concurrency_wave(wave_name, items, profile, problem):
    num_items = len(items)
    print(f"\n--- Starting {wave_name}: {num_items} Simultaneous Submissions ---")

    subs = []
    for item in items:
        lang = Language.objects.get(key=item['lang_key'])
        sub = Submission.objects.create(
            user=profile,
            problem=problem,
            language=lang,
            status='QU',
        )
        SubmissionSource.objects.create(submission=sub, source=item['code'].strip())
        subs.append({
            'sub': sub,
            'id': sub.id,
            'lang_key': item['lang_key'],
            'exp_result': item['exp_result'],
            'exp_status': item['exp_status'],
            'name': item['name'],
            't_dispatched': None,
            'dispatch_latency': None,
            't_started': None,
            't_finished': None,
            'final_status': None,
            'final_result': None,
            'points': None,
            'time': None,
            'memory': None,
            'passed': False,
        })

    db.connection.close()

    barrier = threading.Barrier(num_items)
    dispatch_errors = []

    def dispatch_worker(info):
        sub_id = info['id']
        barrier.wait()
        t0 = time.time()
        try:
            local_sub = Submission.objects.get(id=sub_id)
            success = judge_submission(local_sub)
            t1 = time.time()
            info['t_dispatched'] = t1
            info['dispatch_latency'] = t1 - t0
            if not success:
                dispatch_errors.append((sub_id, "judge_submission returned False"))
        except Exception as e:
            dispatch_errors.append((sub_id, str(e)))
        finally:
            db.connection.close()

    t_barrier_start = time.time()
    threads = [threading.Thread(target=dispatch_worker, args=(info,)) for info in subs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"All {num_items} submissions dispatched to bridge in {time.time() - t_barrier_start:.4f}s.")
    if dispatch_errors:
        print(f"WARNING: Dispatch errors encountered: {dispatch_errors}")
    else:
        print(f"SUCCESS: 100% ({num_items}/{num_items}) dispatch requests acknowledged by bridge.")

    pending_ids = set(info['id'] for info in subs)
    info_map = {info['id']: info for info in subs}
    start_poll = time.time()
    max_timeout = 90.0

    queue_depth_history = []

    while pending_ids and (time.time() - start_poll < max_timeout):
        now = time.time()
        with connection.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(subs))
            cursor.execute(f"""
                SELECT id, status, result, points, time, memory
                FROM judge_submission
                WHERE id IN ({format_strings})
            """, [info['id'] for info in subs])
            rows = cursor.fetchall()

        qu_count = 0
        p_or_g_count = 0
        d_or_ce_count = 0

        for row in rows:
            sid, status, result, points, sub_time, memory = row
            info = info_map[sid]

            if status != 'QU' and info['t_started'] is None:
                info['t_started'] = now

            if status in ('D', 'CE'):
                if sid in pending_ids:
                    info['t_finished'] = now
                    info['final_status'] = status
                    info['final_result'] = result or (status if status == 'CE' else None)
                    info['points'] = points
                    info['time'] = sub_time
                    info['memory'] = memory
                    pending_ids.remove(sid)
                d_or_ce_count += 1
            elif status in ('P', 'G'):
                p_or_g_count += 1
            elif status == 'QU':
                qu_count += 1

        queue_depth_history.append((now - start_poll, qu_count, p_or_g_count, d_or_ce_count))

        if pending_ids:
            time.sleep(0.25)

    total_duration = time.time() - start_poll
    print(f"Batch processing completed in {total_duration:.2f}s.")

    all_passed = True
    print("\n--- Concurrency Batch Results ---")
    for info in subs:
        exp_res = info['exp_result']
        exp_stat = info['exp_status']
        act_res = info['final_result']
        act_stat = info['final_status']

        passed = (act_stat == exp_stat) and (act_res == exp_res)
        info['passed'] = passed
        if not passed:
            all_passed = False

        q_wait = (info['t_started'] - info['t_dispatched']) if (info['t_started'] and info['t_dispatched']) else 0.0
        exec_t = (info['t_finished'] - info['t_started']) if (info['t_finished'] and info['t_started']) else 0.0
        total_t = (info['t_finished'] - info['t_dispatched']) if (info['t_finished'] and info['t_dispatched']) else 0.0

        disp_lat_ms = (info['dispatch_latency'] * 1000) if info['dispatch_latency'] else 0.0

        status_str = "PASS" if passed else "FAIL"
        print(f"[{status_str}] Sub #{info['id']:<3} | {info['name']:<10} | Exp: {exp_res:<3} | Got: {str(act_res):<3} ({act_stat}) | Disp: {disp_lat_ms:>5.1f}ms | QueueWait: {q_wait:>5.2f}s | Exec: {exec_t:>5.2f}s | Total: {total_t:>5.2f}s | Pts: {str(info['points']):>4}")

    return {
        'all_passed': all_passed,
        'duration': total_duration,
        'dispatch_errors': dispatch_errors,
        'subs': subs,
        'queue_history': queue_depth_history,
    }

def main():
    print("=" * 90)
    print("DMOJ Concurrency, Queueing, and Resilience Verification Harness")
    print("=" * 90)

    # 1. Environment & Judge Connection Check
    judge = Judge.objects.filter(online=True).first()
    if not judge:
        print("FATAL: No judge is currently online!")
        sys.exit(1)
    print(f"Connected Online Judge: {judge.name} | Load: {judge.load} | Ping: {judge.ping:.4f}ms")

    problem = Problem.objects.filter(code='aplusb').first()
    if not problem:
        print("FATAL: Problem 'aplusb' not found!")
        sys.exit(1)

    profile = Profile.objects.filter(user__is_superuser=True).first() or Profile.objects.first()

    bridge_pid = get_bridge_pid()
    print(f"Bridge Daemon PID: {bridge_pid}")

    metrics_before = check_process_metrics(bridge_pid)
    print(f"Initial Bridge Open FDs: {metrics_before.get('bridge_open_fds')}")

    # =========================================================================
    # Phase 1: 12 Simultaneous Multi-Language Submissions (Barrier Flood)
    # =========================================================================
    wave1_items = []
    for lang_key, exp_result, exp_status, name, code in TEST_CASES:
        wave1_items.append({
            'lang_key': lang_key,
            'exp_result': exp_result,
            'exp_status': exp_status,
            'name': name,
            'code': code,
        })

    res_wave1 = run_concurrency_wave("Wave 1 (12 Simultaneous Flood Across PY3, CPP20, JAVA8)",
                                     wave1_items, profile, problem)

    metrics_mid = check_process_metrics(bridge_pid)
    print(f"Post-Wave 1 Bridge Open FDs: {metrics_mid.get('bridge_open_fds')}")

    # =========================================================================
    # Phase 2: Rapid-Fire Stream (10 Submissions Dispatched with 50ms Spacing)
    # =========================================================================
    wave2_specs = [
        ("PY3", "AC", "D", "W2_PY3_AC1", TEST_CASES[0][4]),
        ("CPP20", "AC", "D", "W2_CPP_AC1", TEST_CASES[4][4]),
        ("JAVA8", "AC", "D", "W2_JAV_AC1", TEST_CASES[8][4]),
        ("PY3", "WA", "D", "W2_PY3_WA", TEST_CASES[1][4]),
        ("CPP20", "WA", "D", "W2_CPP_WA", TEST_CASES[5][4]),
        ("PY3", "CE", "CE", "W2_PY3_CE", TEST_CASES[3][4]),
        ("CPP20", "CE", "CE", "W2_CPP_CE", TEST_CASES[7][4]),
        ("JAVA8", "CE", "CE", "W2_JAV_CE", TEST_CASES[11][4]),
        ("CPP20", "AC", "D", "W2_CPP_AC2", TEST_CASES[4][4]),
        ("PY3", "AC", "D", "W2_PY3_AC2", TEST_CASES[0][4]),
    ]
    wave2_items = [{
        'lang_key': item[0],
        'exp_result': item[1],
        'exp_status': item[2],
        'name': item[3],
        'code': item[4],
    } for item in wave2_specs]

    res_wave2 = run_concurrency_wave("Wave 2 (10 Rapid-Fire Stream Submissions)",
                                     wave2_items, profile, problem)

    # Let bridge and runner settle
    time.sleep(1.0)

    metrics_after = check_process_metrics(bridge_pid)
    print(f"Post-Wave 2 Bridge Open FDs: {metrics_after.get('bridge_open_fds')}")

    # =========================================================================
    # Phase 3: MariaDB Transaction Integrity & Consistency Inspection
    # =========================================================================
    print("\n" + "=" * 90)
    print("Phase 3: Database Transaction Integrity & Lock Verification")
    print("=" * 90)

    all_tested_sub_ids = [s['id'] for s in res_wave1['subs']] + [s['id'] for s in res_wave2['subs']]

    with connection.cursor() as cursor:
        cursor.execute("SHOW ENGINE INNODB STATUS")
        innodb_status_row = cursor.fetchone()
        innodb_status = innodb_status_row[2] if (innodb_status_row and len(innodb_status_row) > 2) else ""
        has_deadlock = "LATEST DETECTED DEADLOCK" in innodb_status
        print(f"InnoDB Status Deadlock Check: {'DEADLOCK DETECTED!' if has_deadlock else 'NO DEADLOCKS DETECTED (Clean)'}")

        cursor.execute(f"""
            SELECT id, status, result FROM judge_submission
            WHERE id IN ({','.join(['%s']*len(all_tested_sub_ids))}) AND status IN ('QU', 'P', 'G')
        """, all_tested_sub_ids)
        stuck_subs = cursor.fetchall()
        print(f"Tested Submissions Stuck in QU/P/G: {len(stuck_subs)} (Expected: 0)")
        if stuck_subs:
            for s in stuck_subs:
                print(f"  STUCK: Sub #{s[0]} status={s[1]} result={s[2]}")

        format_strings = ','.join(['%s'] * len(all_tested_sub_ids))
        cursor.execute(f"""
            SELECT s.id, s.result, s.points, s.status, COUNT(tc.id) as tc_count,
                   COALESCE(SUM(tc.points), 0) as tc_points_sum
            FROM judge_submission s
            LEFT JOIN judge_submissiontestcase tc ON s.id = tc.submission_id
            WHERE s.id IN ({format_strings})
            GROUP BY s.id, s.result, s.points, s.status
            ORDER BY s.id ASC
        """, all_tested_sub_ids)
        integrity_rows = cursor.fetchall()

    integrity_errors = []
    print(f"\nVerified {len(integrity_rows)} submissions for relational and score consistency:")
    for row in integrity_rows:
        sid, result, points, status, tc_count, tc_sum = row
        if result == 'AC':
            if tc_count != 3 or abs(float(points) - 100.0) > 0.01:
                integrity_errors.append(f"Sub #{sid} AC mismatch: tc_count={tc_count}, points={points}")
        elif result in ('WA', 'TLE'):
            if tc_count < 1 or abs(float(points) - 0.0) > 0.01:
                integrity_errors.append(f"Sub #{sid} {result} mismatch: tc_count={tc_count}, points={points}")
        elif status == 'CE':
            if tc_count != 0:
                integrity_errors.append(f"Sub #{sid} CE has testcases: tc_count={tc_count}")

    if integrity_errors:
        print(f"INTEGRITY ERRORS FOUND: {len(integrity_errors)}")
        for err in integrity_errors:
            print(f"  {err}")
    else:
        print("SUCCESS: 100% of tested submissions have consistent relational and testcase data.")

    # =========================================================================
    # Phase 4: Container & Host Process Health (Zombie Process Check)
    # =========================================================================
    print("\n" + "=" * 90)
    print("Phase 4: Process Health & Zombie Process Detection")
    print("=" * 90)

    docker_top = metrics_after.get('docker_top', '')
    print("Current processes inside dmoj-judge-runner Docker container:")
    print(docker_top)

    zombie_indicators = ['cptbox', 'gcc', 'g++', 'javac', 'java', 'python3']
    lingering_zombies = []
    for line in docker_top.splitlines():
        for z in zombie_indicators:
            if z in line:
                lingering_zombies.append(line.strip())

    if lingering_zombies:
        print(f"WARNING: Potential lingering child processes inside container: {lingering_zombies}")
    else:
        print("SUCCESS: Zero orphaned compiler or sandbox processes inside container.")

    print(f"\nBridge Daemon Process Info:")
    print(metrics_after.get('bridge_ps', 'N/A'))
    fd_growth = None
    if isinstance(metrics_after.get('bridge_open_fds'), int) and isinstance(metrics_before.get('bridge_open_fds'), int):
        fd_growth = metrics_after['bridge_open_fds'] - metrics_before['bridge_open_fds']
        print(f"FD Count: Initial={metrics_before['bridge_open_fds']} -> Final={metrics_after['bridge_open_fds']} (delta: {fd_growth})")

    # =========================================================================
    # Phase 5: Container Recovery & Auto-Reconnection Resilience Test
    # =========================================================================
    print("\n" + "=" * 90)
    print("Phase 5: Judge Container Recovery & Auto-Reconnection Test")
    print("=" * 90)

    print("Restarting dmoj-judge-runner container via docker restart...")
    t_restart_start = time.time()
    res = subprocess.run(['docker', 'restart', 'dmoj-judge-runner'], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR restarting container: {res.stderr}")
        recovery_passed = False
    else:
        print(f"Container restarted in {time.time() - t_restart_start:.2f}s. Waiting for judge to reconnect...")
        reconnected = False
        for attempt in range(25):
            time.sleep(1.0)
            db.connection.close()
            j = Judge.objects.filter(name='default').first()
            if j and j.online:
                print(f"Judge reconnected successfully! (Attempt {attempt+1}, Ping: {j.ping:.4f}ms, Load: {j.load})")
                reconnected = True
                break

        if not reconnected:
            print("ERROR: Judge failed to reconnect within 25 seconds!")
            recovery_passed = False
        else:
            # Dispatch a post-reconnect submission
            print("Dispatching post-recovery validation submission (PY3 AC)...")
            sub_rec = Submission.objects.create(
                user=profile,
                problem=problem,
                language=Language.objects.get(key='PY3'),
                status='QU',
            )
            SubmissionSource.objects.create(submission=sub_rec, source=TEST_CASES[0][4].strip())
            judge_submission(sub_rec)

            # Wait for grading
            t_rec_start = time.time()
            while time.time() - t_rec_start < 15.0:
                sub_rec.refresh_from_db()
                if sub_rec.status not in ('QU', 'P', 'G'):
                    break
                time.sleep(0.3)

            sub_rec.refresh_from_db()
            recovery_passed = (sub_rec.status == 'D' and sub_rec.result == 'AC')
            print(f"Post-recovery submission #{sub_rec.id} result: {sub_rec.result} (status: {sub_rec.status}) -> {'PASS' if recovery_passed else 'FAIL'}")

    # =========================================================================
    # Final Verdict & Report Output
    # =========================================================================
    print("\n" + "=" * 90)
    print("FINAL CONCURRENCY & RESILIENCE SUMMARY")
    print("=" * 90)
    w1_passed = sum(1 for s in res_wave1['subs'] if s['passed'])
    w1_total = len(res_wave1['subs'])
    w2_passed = sum(1 for s in res_wave2['subs'] if s['passed'])
    w2_total = len(res_wave2['subs'])

    print(f"Wave 1 (12 Simultaneous Flood): {w1_passed}/{w1_total} PASSED (Duration: {res_wave1['duration']:.2f}s)")
    print(f"Wave 2 (10 Rapid-Fire Stream):   {w2_passed}/{w2_total} PASSED (Duration: {res_wave2['duration']:.2f}s)")
    print(f"Total Submissions Tested:        {w1_total + w2_total + (1 if recovery_passed else 0)}")
    print(f"Total Submissions Passed:        {w1_passed + w2_passed + (1 if recovery_passed else 0)}")
    print(f"Database Integrity Check:        {'PASSED' if not integrity_errors and not has_deadlock and not stuck_subs else 'FAILED'}")
    print(f"Zombie Process Check:            {'PASSED' if not lingering_zombies else 'FAILED'}")
    print(f"Container Recovery Check:        {'PASSED' if recovery_passed else 'FAILED'}")

    overall_success = (
        res_wave1['all_passed'] and
        res_wave2['all_passed'] and
        not integrity_errors and
        not has_deadlock and
        not stuck_subs and
        not lingering_zombies and
        recovery_passed
    )

    result_json = {
        'overall_success': overall_success,
        'wave1': {
            'total': w1_total,
            'passed': w1_passed,
            'duration': res_wave1['duration'],
            'submissions': [{
                'id': s['id'], 'name': s['name'], 'lang': s['lang_key'],
                'expected': s['exp_result'], 'actual': s['final_result'],
                'dispatch_lat_ms': (s['dispatch_latency'] * 1000) if s['dispatch_latency'] else None,
                'q_wait_s': (s['t_started'] - s['t_dispatched']) if (s['t_started'] and s['t_dispatched']) else None,
                'exec_t_s': (s['t_finished'] - s['t_started']) if (s['t_finished'] and s['t_started']) else None,
                'total_t_s': (s['t_finished'] - s['t_dispatched']) if (s['t_finished'] and s['t_dispatched']) else None,
                'points': float(s['points']) if s['points'] is not None else 0.0,
                'passed': s['passed'],
            } for s in res_wave1['subs']],
            'queue_history': res_wave1['queue_history'],
        },
        'wave2': {
            'total': w2_total,
            'passed': w2_passed,
            'duration': res_wave2['duration'],
            'submissions': [{
                'id': s['id'], 'name': s['name'], 'lang': s['lang_key'],
                'expected': s['exp_result'], 'actual': s['final_result'],
                'points': float(s['points']) if s['points'] is not None else 0.0,
                'passed': s['passed'],
            } for s in res_wave2['subs']],
        },
        'recovery_passed': recovery_passed,
        'metrics_before': metrics_before,
        'metrics_after': metrics_after,
        'fd_growth': fd_growth,
        'has_deadlock': has_deadlock,
        'stuck_count': len(stuck_subs),
        'integrity_errors': integrity_errors,
        'lingering_zombies': lingering_zombies,
    }

    report_path = os.path.join(BASE_DIR, "concurrency_resilience_results.json")
    with open(report_path, "w") as f:
        json.dump(result_json, f, indent=2)
    print(f"\nDetailed metrics written to: {report_path}")

    if not overall_success:
        print("\nOVERALL VERDICT: FAIL")
        sys.exit(1)
    else:
        print("\nOVERALL VERDICT: PASS")

if __name__ == '__main__':
    main()
