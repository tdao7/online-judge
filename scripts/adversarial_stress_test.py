import os
import sys
import time
import json

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.db import connection
from judge.models import Judge, Language, Problem, Profile, Submission, SubmissionSource, SubmissionTestCase

ADVERSARIAL_TESTS = [
    # ---------------- Python 3 ----------------
    {
        "id_tag": "PY3_RTE_DIVZERO",
        "lang": "PY3",
        "category": "Python 3 Runtime Exception",
        "name": "ZeroDivisionError -> IR/RTE",
        "code": """
import sys
raw = sys.stdin.read().split()
# Force zero division error immediately
x = 42 // 0
print(x)
""",
        "allowed_results": ["IR", "RTE"],
        "expected_status": "D",
        "description": "Trigger unhandled ZeroDivisionError exception in Python 3",
    },
    {
        "id_tag": "PY3_TLE_LOOP",
        "lang": "PY3",
        "category": "Python 3 Infinite Loop TLE",
        "name": "Infinite Loop Clean TLE",
        "code": """
import sys
raw = sys.stdin.read().split()
while True:
    pass
""",
        "allowed_results": ["TLE"],
        "expected_status": "D",
        "description": "Clean CPU-bound busy-wait loop exceeding 2.0s time limit",
    },
    {
        "id_tag": "PY3_RTE_RECURSION_DEFAULT",
        "lang": "PY3",
        "category": "Python 3 Recursion Limit Exception",
        "name": "RecursionError (IR/RTE)",
        "code": """
def blowup(n):
    return blowup(n + 1)
blowup(0)
""",
        "allowed_results": ["IR", "RTE"],
        "expected_status": "D",
        "description": "Standard unhandled RecursionError exception without custom limit",
    },
    {
        "id_tag": "PY3_RTE_RECURSION_DEEP",
        "lang": "PY3",
        "category": "Python 3 Recursion Depth / Memory",
        "name": "Deep Recursion Stack / Memory Exhaustion",
        "code": """
import sys
sys.setrecursionlimit(2000000)
def deep_blowup(n):
    return deep_blowup(n + 1) + 1
deep_blowup(0)
""",
        "allowed_results": ["MLE", "RTE", "IR"],
        "expected_status": "D",
        "description": "Exceed C-stack depth with elevated recursion limit causing SIGSEGV, MLE or RecursionError",
    },
    {
        "id_tag": "PY3_MLE_MEMORY",
        "lang": "PY3",
        "category": "Python 3 Memory Allocation",
        "name": "Memory Limit Exceeded Bomb",
        "code": """
import sys
chunks = []
# Problem memory limit is 65536 KB (64 MB)
for _ in range(50):
    chunks.append(b"A" * (5 * 1024 * 1024))
print(len(chunks))
""",
        "allowed_results": ["MLE", "IR", "RTE"],
        "expected_status": "D",
        "description": "Exceed 64MB memory limit via rapid heap byte allocations",
    },
    {
        "id_tag": "PY3_AC_BASELINE",
        "lang": "PY3",
        "category": "Python 3 Accepted Baseline",
        "name": "Standard Python 3 AC Solution",
        "code": """
import sys
raw = sys.stdin.read().split()
if raw:
    n = int(raw[0])
    idx = 1
    for _ in range(n):
        print(int(raw[idx]) + int(raw[idx+1]))
        idx += 2
""",
        "allowed_results": ["AC"],
        "expected_status": "D",
        "description": "Correct solution solving all 3 testcases for full 100 points",
    },

    # ---------------- C++20 ----------------
    {
        "id_tag": "CPP20_RTE_NULLPTR",
        "lang": "CPP20",
        "category": "C++20 SIGSEGV Null Pointer Dereference",
        "name": "Null Pointer Dereference (SIGSEGV)",
        "code": """
#include <iostream>
int main() {
    volatile int* p = nullptr;
    *p = 42;
    return 0;
}
""",
        "allowed_results": ["RTE"],
        "expected_status": "D",
        "description": "Direct null pointer dereference triggering SIGSEGV signal (status bit 2)",
    },
    {
        "id_tag": "CPP20_TLE_LOOP",
        "lang": "CPP20",
        "category": "C++20 Infinite Loop TLE",
        "name": "Infinite Volatile Loop TLE",
        "code": """
#include <iostream>
int main() {
    volatile long long counter = 0;
    while (true) {
        counter++;
    }
    return 0;
}
""",
        "allowed_results": ["TLE"],
        "expected_status": "D",
        "description": "Volatile counter infinite loop exceeding 2.0s time limit",
    },
    {
        "id_tag": "CPP20_RTE_STACK_OVERFLOW",
        "lang": "CPP20",
        "category": "C++20 Stack Allocation Overflow",
        "name": "128MB Stack Array Allocation (SIGSEGV)",
        "code": """
#include <iostream>
int main() {
    volatile char buffer[128 * 1024 * 1024];
    buffer[0] = 'X';
    std::cout << buffer[0] << std::endl;
    return 0;
}
""",
        "allowed_results": ["RTE", "MLE"],
        "expected_status": "D",
        "description": "Oversized stack buffer allocation triggering immediate guard-page SIGSEGV",
    },
    {
        "id_tag": "CPP20_CE_MISSING_HEADER",
        "lang": "CPP20",
        "category": "C++20 Header Compilation Error",
        "name": "Non-existent Header Inclusion (CE)",
        "code": """
#include <non_existent_adversarial_header_xyz_123.hpp>
#include <iostream>
int main() {
    std::cout << "Unreachable" << std::endl;
    return 0;
}
""",
        "allowed_results": ["CE"],
        "expected_status": "CE",
        "description": "Include missing header producing fatal compilation error recorded in submission.error",
    },
    {
        "id_tag": "CPP20_RTE_SIGFPE",
        "lang": "CPP20",
        "category": "C++20 Division by Zero (SIGFPE)",
        "name": "Division by Zero (SIGFPE)",
        "code": """
#include <iostream>
#include <csignal>
int main() {
    std::raise(SIGFPE);
    return 0;
}
""",
        "allowed_results": ["RTE"],
        "expected_status": "D",
        "description": "Integer division by zero triggering SIGFPE signal (status bit 2)",
    },
    {
        "id_tag": "CPP20_AC_BASELINE",
        "lang": "CPP20",
        "category": "C++20 Accepted Baseline",
        "name": "Fast I/O C++20 AC Solution",
        "code": """
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
""",
        "allowed_results": ["AC"],
        "expected_status": "D",
        "description": "Standard fast I/O C++20 solution scoring 100/100 points",
    },

    # ---------------- Java 8 ----------------
    {
        "id_tag": "JAVA8_RTE_NPE",
        "lang": "JAVA8",
        "category": "Java 8 NullPointerException",
        "name": "NullPointerException (IR/RTE)",
        "code": """
public class aplusb {
    public static void main(String[] args) {
        String s = null;
        System.out.println("Length: " + s.length());
    }
}
""",
        "allowed_results": ["IR", "RTE"],
        "expected_status": "D",
        "description": "Dereference null reference in Java 8 resulting in unhandled NullPointerException",
    },
    {
        "id_tag": "JAVA8_RTE_AIOOB",
        "lang": "JAVA8",
        "category": "Java 8 Array Index Out of Bounds",
        "name": "ArrayIndexOutOfBoundsException (IR/RTE)",
        "code": """
public class aplusb {
    public static void main(String[] args) {
        int[] arr = new int[2];
        arr[0] = 10;
        arr[1] = 20;
        System.out.println("Element: " + arr[10]);
    }
}
""",
        "allowed_results": ["IR", "RTE"],
        "expected_status": "D",
        "description": "Access out-of-bounds index 10 on array size 2 resulting in unhandled exception",
    },
    {
        "id_tag": "JAVA8_CE_SYNTAX",
        "lang": "JAVA8",
        "category": "Java 8 Syntax Compilation Error",
        "name": "Malformed Class Body Syntax (CE)",
        "code": """
public class aplusb {
    public static void main(String[] args) {
        int x = ; // illegal expression syntax
    }
}
""",
        "allowed_results": ["CE"],
        "expected_status": "CE",
        "description": "Malformed variable assignment syntax triggering javac compilation failure",
    },
    {
        "id_tag": "JAVA8_TLE_LOOP",
        "lang": "JAVA8",
        "category": "Java 8 Infinite Loop TLE",
        "name": "Infinite While Loop (TLE)",
        "code": """
public class aplusb {
    public static void main(String[] args) {
        long c = 0;
        while (true) {
            c++;
        }
    }
}
""",
        "allowed_results": ["TLE"],
        "expected_status": "D",
        "description": "Infinite while loop in Java 8 exceeding 2.0s time limit",
    },
    {
        "id_tag": "JAVA8_RTE_STACKOVERFLOW",
        "lang": "JAVA8",
        "category": "Java 8 StackOverflowError",
        "name": "StackOverflowError (IR/RTE)",
        "code": """
public class aplusb {
    static void blowup() {
        blowup();
    }
    public static void main(String[] args) {
        blowup();
    }
}
""",
        "allowed_results": ["IR", "RTE"],
        "expected_status": "D",
        "description": "Infinite recursion in Java 8 resulting in unhandled StackOverflowError",
    },
    {
        "id_tag": "JAVA8_AC_BASELINE",
        "lang": "JAVA8",
        "category": "Java 8 Accepted Baseline",
        "name": "Java 8 Scanner/BufferedReader AC Solution",
        "code": """
import java.io.*;
import java.util.*;
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
""",
        "allowed_results": ["AC"],
        "expected_status": "D",
        "description": "Valid Java 8 implementation scoring 100/100 points",
    },
]

def run_stress_suite():
    print("=" * 90)
    print("DMOJ Empirical Adversarial Stress Test Suite (Milestone 1 Challenger)")
    print("=" * 90)

    judge = Judge.objects.filter(online=True).first()
    if not judge:
        print("ERROR: Judge is offline! Bridge or judge-tier1 container not running.")
        sys.exit(1)
    print(f"Connected Online Judge: {judge.name} | Load: {judge.load} | Ping: {judge.ping:.4f}ms")

    problem = Problem.objects.filter(code='aplusb').first()
    if not problem:
        print("ERROR: Problem 'aplusb' not found!")
        sys.exit(1)

    profile = Profile.objects.filter(user__is_superuser=True).first() or Profile.objects.first()

    summary_records = []
    overall_passed = True

    for test in ADVERSARIAL_TESTS:
        lang = Language.objects.get(key=test['lang'])
        sub = Submission.objects.create(
            user=profile,
            problem=problem,
            language=lang,
            status='QU',
        )
        SubmissionSource.objects.create(submission=sub, source=test['code'].strip())

        # Submit to judge daemon
        sub.judge(force_judge=True)

        # Wait for completion (timeout 30s)
        start_t = time.time()
        timeout = 30.0
        while time.time() - start_t < timeout:
            sub.refresh_from_db()
            if sub.status not in ('QU', 'P', 'G'):
                break
            time.sleep(0.4)

        sub.refresh_from_db()
        actual_result = sub.result or (sub.status if sub.status == 'CE' else None)
        passed = (sub.status == test['expected_status']) and (actual_result in test['allowed_results'])

        if not passed:
            overall_passed = False

        # Query testcases
        tcs = list(SubmissionTestCase.objects.filter(submission=sub).order_by('case').values(
            'case', 'status', 'time', 'memory', 'points', 'total', 'feedback', 'extended_feedback'
        ))

        time_val = f"{sub.time:.3f}s" if sub.time is not None else "N/A"
        mem_val = f"{sub.memory:.0f}KB" if sub.memory is not None else "N/A"
        pts_val = f"{sub.points if sub.points is not None else 0.0:.1f}"

        record = {
            "sub_id": sub.id,
            "id_tag": test['id_tag'],
            "lang": test['lang'],
            "name": test['name'],
            "expected_status": test['expected_status'],
            "allowed_results": test['allowed_results'],
            "actual_status": sub.status,
            "actual_result": actual_result,
            "passed": passed,
            "time": time_val,
            "memory": mem_val,
            "points": pts_val,
            "error_snippet": (sub.error or "")[:200].replace("\n", " ") if sub.error else "",
            "testcases": tcs,
        }
        summary_records.append(record)

        verdict_str = f"{actual_result} (status: {sub.status})"
        expected_str = f"{'/'.join(test['allowed_results'])} ({test['expected_status']})"
        status_flag = "PASS" if passed else "FAIL"

        print(f"[{status_flag}] Sub #{sub.id:<3} | {test['lang']:<5} | {test['name']:<40} | Got: {verdict_str:<12} | Exp: {expected_str:<12} | {time_val:>7} | {mem_val:>9}")
        if sub.error:
            err_line = sub.error.strip().split("\n")[0][:80]
            print(f"       -> Compile Error: {err_line}")
        if tcs:
            tc_detail = " | ".join([f"Case {tc['case']}: {tc['status']} ({tc['points']}/{tc['total']}pts, {tc['time']}s, {tc['memory']}KB)" for tc in tcs])
            print(f"       -> Testcases: {tc_detail}")

    print("\n" + "=" * 90)
    passed_count = sum(1 for r in summary_records if r['passed'])
    total_count = len(summary_records)
    print(f"Final Empirical Adversarial Test Results: {passed_count}/{total_count} PASSED")
    print("=" * 90)

    # Output detailed JSON report for inspection and database validation
    json_path = os.path.join(BASE_DIR, "adversarial_test_results.json")
    with open(json_path, "w") as f:
        json.dump(summary_records, f, indent=2)
    print(f"Detailed JSON results written to: {json_path}")

    # MariaDB Direct SQL verification
    print("\nExecuting Direct MariaDB SQL Verification Queries:")
    with connection.cursor() as cursor:
        sub_ids = [r['sub_id'] for r in summary_records]
        format_strings = ','.join(['%s'] * len(sub_ids))
        cursor.execute(f"""
            SELECT s.id, s.language_id, l.key, s.status, s.result, s.time, s.memory, s.points, s.judged_on_id, s.error
            FROM judge_submission s
            JOIN judge_language l ON s.language_id = l.id
            WHERE s.id IN ({format_strings})
            ORDER BY s.id ASC
        """, sub_ids)
        rows = cursor.fetchall()
        print(f"Found {len(rows)} raw rows in judge_submission:")
        for row in rows:
            err_peek = (row[9][:40] + "...") if row[9] else "None"
            print(f"  SQL Row: Sub #{row[0]} | Lang: {row[2]} | Status: {row[3]} | Result: {row[4]} | Time: {row[5]} | Mem: {row[6]} | Pts: {row[7]} | JudgedOn: {row[8]} | Error: {err_peek}")

        cursor.execute(f"""
            SELECT tc.submission_id, tc.case, tc.status, tc.time, tc.memory, tc.points, tc.feedback
            FROM judge_submissiontestcase tc
            WHERE tc.submission_id IN ({format_strings})
            ORDER BY tc.submission_id ASC, tc.case ASC
        """, sub_ids)
        tc_rows = cursor.fetchall()
        print(f"Found {len(tc_rows)} raw rows in judge_submissiontestcase:")
        for tc in tc_rows:
            print(f"  SQL TC Row: Sub #{tc[0]} | Case: {tc[1]} | Status: {tc[2]} | Time: {tc[3]} | Mem: {tc[4]} | Pts: {tc[5]} | Feedback: {tc[6]}")

    if not overall_passed:
        print("\nADVERSARIAL STRESS TEST FAILED!")
        sys.exit(1)
    else:
        print("\nADVERSARIAL STRESS TEST PASSED 100%!")

if __name__ == "__main__":
    run_stress_suite()
