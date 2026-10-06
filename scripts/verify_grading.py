import os
import sys
import time

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from judge.models import Judge, Language, Problem, Profile, Submission, SubmissionSource

TEST_SUITE = [
    # Language, Expected Result, Expected Status, Name, Code
    ("PY3", "AC", "D", "Python 3 AC", """
import sys
raw = sys.stdin.read().split()
if raw:
    n = int(raw[0])
    idx = 1
    for _ in range(n):
        print(int(raw[idx]) + int(raw[idx+1]))
        idx += 2
"""),
    ("PY3", "WA", "D", "Python 3 WA", """
import sys
raw = sys.stdin.read().split()
if raw:
    n = int(raw[0])
    for _ in range(n):
        print(0)
"""),
    ("PY3", "TLE", "D", "Python 3 TLE", """
while True:
    pass
"""),
    ("PY3", "CE", "CE", "Python 3 CE", """
def broken_syntax(
"""),
    ("CPP20", "AC", "D", "C++20 AC", """
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
    ("CPP20", "WA", "D", "C++20 WA", """
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
    ("CPP20", "TLE", "D", "C++20 TLE", """
#include <iostream>
int main() {
    volatile long long x = 0;
    while (true) x++;
    return 0;
}
"""),
    ("CPP20", "CE", "CE", "C++20 CE", """
#include <iostream>
int main() {
    SYNTAX_ERROR_UNDEFINED_VARIABLE = 42;
    return 0;
}
"""),
    ("JAVA8", "AC", "D", "Java 8 AC", """
import java.io.*;
import java.util.*;
public class aplusb {
    public static void main(String[] args) throws IOException {
        BufferedReader cin = new BufferedReader(new InputStreamReader(System.in));
        String line = cin.readLine();
        if (line == null) return;
        int n = Integer.parseInt(line.trim());
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(cin.readLine());
            System.out.println(Integer.parseInt(st.nextToken()) + Integer.parseInt(st.nextToken()));
        }
    }
}
"""),
    ("JAVA8", "WA", "D", "Java 8 WA", """
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
    ("JAVA8", "TLE", "D", "Java 8 TLE", """
public class aplusb {
    public static void main(String[] args) {
        while (true) {}
    }
}
"""),
    ("JAVA8", "CE", "CE", "Java 8 CE", """
public class aplusb {
    public static void main(String[] args) {
        SYNTAX_ERROR_UNDEFINED_VARIABLE = 42;
    }
}
"""),
    ("GO", "AC", "D", "Go AC", """
package main
import (
    "bufio"
    "fmt"
    "os"
)
func main() {
    reader := bufio.NewReader(os.Stdin)
    var n int
    if _, err := fmt.Fscan(reader, &n); err != nil {
        return
    }
    writer := bufio.NewWriter(os.Stdout)
    defer writer.Flush()
    for i := 0; i < n; i++ {
        var a, b int
        fmt.Fscan(reader, &a, &b)
        fmt.Fprintln(writer, a+b)
    }
}
"""),
    ("RUST", "AC", "D", "Rust AC", """
use std::io::{self, Read, Write, BufWriter};
fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut tokens = input.split_whitespace();
    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());
    if let Some(n_str) = tokens.next() {
        if let Ok(n) = n_str.parse::<usize>() {
            for _ in 0..n {
                if let (Some(a_str), Some(b_str)) = (tokens.next(), tokens.next()) {
                    let a: i64 = a_str.parse().unwrap();
                    let b: i64 = b_str.parse().unwrap();
                    writeln!(out, "{}", a + b).unwrap();
                }
            }
        }
    }
}
"""),
    ("C", "AC", "D", "C AC", """
#include <stdio.h>
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    while (n--) {
        long long a, b;
        scanf("%lld %lld", &a, &b);
        printf("%lld\\n", a + b);
    }
    return 0;
}
"""),
    ("PYPY3", "AC", "D", "PyPy 3 AC", """
import sys
data = sys.stdin.read().split()
if data:
    n = int(data[0])
    idx = 1
    out = []
    for _ in range(n):
        out.append(str(int(data[idx]) + int(data[idx+1])))
        idx += 2
    sys.stdout.write('\\n'.join(out) + '\\n')
"""),
]

def run_test_harness():
    print("=" * 80)
    print("DMOJ Multi-Language Grading Verification Harness")
    print("=" * 80)

    judge = Judge.objects.filter(online=True).first()
    if not judge:
        print("ERROR: No judge is currently online! Start bridge and judge container first.")
        sys.exit(1)
    print(f"Connected Online Judge: {judge.name} (Load: {judge.load}, Ping: {judge.ping:.4f}ms)")

    problem = Problem.objects.filter(code='aplusb').first()
    if not problem:
        print("ERROR: Problem 'aplusb' not found in database! Load demo fixture first.")
        sys.exit(1)

    profile = Profile.objects.filter(user__is_superuser=True).first()
    if not profile:
        profile = Profile.objects.first()

    results = []
    all_passed = True

    for lang_key, exp_result, exp_status, test_name, code in TEST_SUITE:
        lang = Language.objects.get(key=lang_key)
        sub = Submission.objects.create(
            user=profile,
            problem=problem,
            language=lang,
            status='QU',
        )
        SubmissionSource.objects.create(submission=sub, source=code.strip())

        # Trigger grading
        sub.judge(force_judge=True)

        # Poll until graded (timeout: 55s)
        start_t = time.time()
        while time.time() - start_t < 55:
            sub.refresh_from_db()
            if sub.status not in ('QU', 'P', 'G'):
                break
            time.sleep(0.5)

        sub.refresh_from_db()
        actual_result = sub.result or (sub.status if sub.status in ('CE', 'QU', 'P', 'G') else 'N/A')
        passed = (sub.status == exp_status) and (actual_result == exp_result)
        if not passed:
            all_passed = False

        time_str = f"{sub.time:.3f}s" if sub.time is not None else "0.000s"
        mem_str = f"{sub.memory:.0f}KB" if sub.memory is not None else "0KB"
        points_str = f"{sub.points or 0:.0f}"

        results.append({
            'name': test_name,
            'lang': lang_key,
            'expected': f"{exp_result} ({exp_status})",
            'actual': f"{actual_result} ({sub.status})",
            'time': time_str,
            'memory': mem_str,
            'points': points_str,
            'passed': passed,
            'sub_id': sub.id,
        })
        print(f"[{'PASS' if passed else 'FAIL'}] #{sub.id:<3} {test_name:<16} | Verdict: {actual_result:<3} (Expected: {exp_result:<3}) | Time: {time_str:>7} | Mem: {mem_str:>8} | Points: {points_str:>3}")

    print("\n" + "=" * 80)
    print(f"Summary: {sum(1 for r in results if r['passed'])}/{len(results)} tests passed.")
    print("=" * 80)

    if not all_passed:
        print("FAILED: Some grading tests did not match expected verdicts.")
        sys.exit(1)
    print(f"SUCCESS: All {len(results)} multi-language grading tests passed with 100% accuracy!")

run_test_harness()
