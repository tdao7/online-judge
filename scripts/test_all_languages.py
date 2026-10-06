import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from judge.models import Problem, Language, Submission, SubmissionSource, Profile

prob = Problem.objects.get(code='aplusb')
user = Profile.objects.filter(user__is_superuser=True).first()
if not user:
    user = Profile.objects.first()

SOLUTIONS = [
    ("C", "C", """#include <stdio.h>
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
    ("C11", "C11", """#include <stdio.h>
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
    ("CPP03", "C++03", """#include <iostream>
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
    ("CPP11", "C++11", """#include <iostream>
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
    ("CPP14", "C++14", """#include <iostream>
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
    ("CPP17", "C++17", """#include <iostream>
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
    ("CPP20", "C++20", """#include <iostream>
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
    ("PY2", "Python 2", """import sys
data = sys.stdin.read().split()
if data:
    n = int(data[0])
    idx = 1
    out = []
    for _ in xrange(n):
        out.append(str(int(data[idx]) + int(data[idx+1])))
        idx += 2
    print '\\n'.join(out)
"""),
    ("PY3", "Python 3", """import sys
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
    ("PYPY3", "PyPy 3", """import sys
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
    ("JAVA", "Java", """import java.io.*;
import java.util.*;
public class aplusb {
    public static void main(String[] args) throws IOException {
        BufferedReader cin = new BufferedReader(new InputStreamReader(System.in));
        String line = cin.readLine();
        if (line == null) return;
        int n = Integer.parseInt(line.trim());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(cin.readLine());
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());
            sb.append(a + b).append("\\n");
        }
        System.out.print(sb.toString());
    }
}
"""),
    ("JAVA8", "Java 8", """import java.io.*;
import java.util.*;
public class aplusb {
    public static void main(String[] args) throws IOException {
        BufferedReader cin = new BufferedReader(new InputStreamReader(System.in));
        String line = cin.readLine();
        if (line == null) return;
        int n = Integer.parseInt(line.trim());
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(cin.readLine());
            long a = Long.parseLong(st.nextToken());
            long b = Long.parseLong(st.nextToken());
            sb.append(a + b).append("\\n");
        }
        System.out.print(sb.toString());
    }
}
"""),
    ("GO", "Go", """package main
import (
    "bufio"
    "fmt"
    "os"
)
func main() {
    reader := bufio.NewReader(os.Stdin)
    writer := bufio.NewWriter(os.Stdout)
    defer writer.Flush()
    var n int
    if _, err := fmt.Fscan(reader, &n); err != nil {
        return
    }
    for i := 0; i < n; i++ {
        var a, b int64
        fmt.Fscan(reader, &a, &b)
        fmt.Fprintln(writer, a+b)
    }
}
"""),
    ("RUST", "Rust", """use std::io::{self, Read, Write, BufWriter};
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
    ("PAS", "Pascal", """program aplusb;
var
    n, i: longint;
    a, b: int64;
begin
    if not eof then
    begin
        readln(n);
        for i := 1 to n do
        begin
            readln(a, b);
            writeln(a + b);
        end;
    end;
end.
"""),
    ("PERL", "Perl", """use strict;
use warnings;
my $n = <STDIN>;
if (defined $n) {
    while (<STDIN>) {
        my @nums = split;
        if (@nums >= 2) {
            print ($nums[0] + $nums[1], "\\n");
        }
    }
}
"""),
    ("AWK", "AWK", """NR > 1 { print $1 + $2 }
"""),
]

print(f"{'Language':<12} | {'Verdict':<8} | {'Status':<6} | {'Time':<8} | {'Points':<6}")
print("-" * 50)
for lang_key, label, src in SOLUTIONS:
    lang_obj = Language.objects.filter(key=lang_key).first()
    if not lang_obj:
        print(f"{label:<12} | SKIP (Not in DB)")
        continue
    sub = Submission.objects.create(
        user=user,
        problem=prob,
        language=lang_obj,
        status='QU',
    )
    SubmissionSource.objects.create(submission=sub, source=src.strip())
    sub.judge(force_judge=True)
    start = time.time()
    while time.time() - start < 45:
        sub.refresh_from_db()
        if sub.status not in ('QU', 'P', 'G'):
            break
        time.sleep(0.3)
    sub.refresh_from_db()
    res = sub.result or sub.status
    t_str = f"{sub.time:.3f}s" if sub.time is not None else "N/A"
    print(f"{label:<12} | {res:<8} | {sub.status:<6} | {t_str:<8} | {sub.points}")
