#!/usr/bin/env python3
"""
scripts/seed_placement_contest.py
Creates the official VCoderLog Placement Test Exam on Arena:
1. Problems:
   - mang: MANG – Tổng hợp mảng một chiều (15đ)
   - vt09: VT09 – Số nguyên tố trong mảng (20đ)
   - maxsum: MAXSUM – Dãy con có tổng lớn nhất (25đ)
   - twosum: TWOSUM – Hai số có tổng bằng S (25đ)
   - taxi158b: 158B – Taxi (Codeforces Greedy) (25đ)
2. Test cases & init.yml for all problems
3. Contest:
   - Key: chuyentin90
   - Name: Kiểm Tra Đầu Vào Lớp Chuyên Tin – VCoderLog
   - Time limit: 90 minutes
   - Points: 85 (or 100 with interview/defense)
"""

import os
import sys
import yaml
import random
import math
from datetime import timedelta
from pathlib import Path

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.utils import timezone
from judge.models import Problem, ProblemGroup, ProblemType, Contest, ContestProblem, Profile

REMOTE_PROBLEMS_DIR = Path("/home/tdao7/dmoj-judge/problems")
LOCAL_PROBLEMS_DIR = JUDGE_ROOT.parent / "problems"
PROBLEMS_DIR = REMOTE_PROBLEMS_DIR if REMOTE_PROBLEMS_DIR.exists() else LOCAL_PROBLEMS_DIR
PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)

def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True

# --- Solvers ---
def solve_mang(data_str):
    lines = [l.strip() for l in data_str.strip().splitlines() if l.strip()]
    if not lines:
        return "0\n0\n-1\n"
    n = int(lines[0])
    parts = []
    for line in lines[1:]:
        parts.extend(line.split())
    arr = [int(x) for x in parts[:n]]
    
    total_sum = sum(arr)
    even_count = sum(1 for x in arr if x % 2 == 0)
    last_pos = -1
    for x in arr:
        if x > 0:
            last_pos = x
    return f"{total_sum}\n{even_count}\n{last_pos}\n"

def solve_vt09(data_str):
    lines = [l.strip() for l in data_str.strip().splitlines() if l.strip()]
    if not lines:
        return "-1\n"
    n = int(lines[0])
    parts = []
    for line in lines[1:]:
        parts.extend(line.split())
    arr = [int(x) for x in parts[:n]]
    
    primes = sorted(list(set(x for x in arr if is_prime(x))))
    if not primes:
        return "-1\n"
    return " ".join(str(x) for x in primes) + "\n"

def solve_maxsum(data_str):
    lines = [l.strip() for l in data_str.strip().splitlines() if l.strip()]
    if not lines:
        return "0\n"
    n = int(lines[0])
    parts = []
    for line in lines[1:]:
        parts.extend(line.split())
    arr = [int(x) for x in parts[:n]]
    
    max_so_far = arr[0]
    curr_max = arr[0]
    for x in arr[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return f"{max_so_far}\n"

def solve_twosum(data_str):
    lines = [l.strip() for l in data_str.strip().splitlines() if l.strip()]
    if not lines:
        return "-1\n"
    first = lines[0].split()
    n, S = int(first[0]), int(first[1])
    parts = []
    for line in lines[1:]:
        parts.extend(line.split())
    arr = [int(x) for x in parts[:n]]
    
    seen = {}
    found = None
    for idx, val in enumerate(arr, 1):
        target = S - val
        if target in seen:
            prev_idx = seen[target]
            candidate = (min(prev_idx, idx), max(prev_idx, idx))
            if found is None or candidate < found:
                found = candidate
        if val not in seen:
            seen[val] = idx
            
    if found:
        return f"{found[0]} {found[1]}\n"
    return "-1\n"

def solve_taxi158b(data_str):
    lines = [l.strip() for l in data_str.strip().splitlines() if l.strip()]
    if not lines:
        return "0\n"
    n = int(lines[0])
    parts = []
    for line in lines[1:]:
        parts.extend(line.split())
    arr = [int(x) for x in parts[:n]]
    
    count = [0] * 5
    for s in arr:
        count[s] += 1
        
    taxis = count[4]
    
    # 3 and 1
    pair_3_1 = min(count[3], count[1])
    taxis += count[3]
    count[1] -= pair_3_1
    
    # 2 and 2
    taxis += count[2] // 2
    count[2] %= 2
    
    if count[2] > 0:
        taxis += 1
        count[1] = max(0, count[1] - 2)
        
    if count[1] > 0:
        taxis += (count[1] + 3) // 4
        
    return f"{taxis}\n"

PROBLEMS_CONFIG = [
    {
        "code": "mang",
        "name": "MANG – Tổng hợp mảng một chiều",
        "points": 15.0,
        "group": "array1d",
        "time_limit": 1.0,
        "memory_limit": 262144,
        "types": ["basic-io", "data-structures"],
        "description": """Cho số nguyên dương $n$ và mảng số nguyên $A = [A_1, A_2, \\dots, A_n]$.

Hãy viết chương trình thực hiện $3$ yêu cầu sau:
1. Tính tổng tất cả các phần tử trong mảng $A$.
2. Đếm số lượng phần tử là số chẵn trong mảng $A$.
3. Tìm phần tử nguyên dương ($> 0$) xuất hiện cuối cùng trong mảng $A$. Nếu mảng không có phần tử nguyên dương nào, in ra `-1`.

### Dữ liệu vào
- Dòng đầu tiên chứa số nguyên dương $n$ ($1 \\le n \\le 10^5$).
- Dòng thứ hai chứa $n$ số nguyên $A_1, A_2, \\dots, A_n$ ($-10^9 \\le A_i \\le 10^9$).

### Dữ liệu ra
- Dòng 1: In ra một số nguyên là tổng các phần tử trong mảng.
- Dòng 2: In ra số lượng phần tử là số chẵn.
- Dòng 3: In ra giá trị của phần tử nguyên dương cuối cùng xuất hiện trong mảng, hoặc `-1` nếu không có.

### Ví dụ
#### Đầu vào:
```
5
-2 4 -5 8 -1
```
#### Đầu ra:
```
4
3
8
```
""",
        "solver": solve_mang,
        "test_generator": lambda i: (
            f"5\n-2 4 -5 8 -1\n" if i == 0 else
            f"4\n-1 -3 -5 -7\n" if i == 1 else
            f"10\n" + " ".join(str(random.randint(-100, 100)) for _ in range(10)) + "\n" if i < 4 else
            f"100\n" + " ".join(str(random.randint(-1000, 1000)) for _ in range(100)) + "\n" if i < 7 else
            f"5000\n" + " ".join(str(random.randint(-10**9, 10**9)) for _ in range(5000)) + "\n"
        )
    },
    {
        "code": "vt09",
        "name": "VT09 – Số nguyên tố trong mảng",
        "points": 20.0,
        "group": "number",
        "time_limit": 1.0,
        "memory_limit": 262144,
        "types": ["number-theory", "sorting"],
        "description": """Cho dãy số nguyên gồm $n$ phần tử $A_1, A_2, \\dots, A_n$.

Hãy tìm tất cả các số nguyên tố có trong dãy số, sau đó in các số nguyên tố này ra màn hình theo thứ tự **tăng dần** và **loại bỏ các giá trị trùng lặp**.

*Lưu ý:* Một số nguyên $p > 1$ được gọi là số nguyên tố nếu nó chỉ có hai ước dương là $1$ và chính nó.

### Dữ liệu vào
- Dòng đầu tiên chứa số nguyên dương $n$ ($1 \\le n \\le 10^5$).
- Dòng thứ hai chứa $n$ số nguyên $A_1, A_2, \\dots, A_n$ ($-10^9 \\le A_i \\le 10^9$).

### Dữ liệu ra
- In ra các số nguyên tố phân biệt theo thứ tự tăng dần, cách nhau bởi một dấu cách.
- Nếu trong dãy không có số nguyên tố nào, in ra `-1`.

### Ví dụ
#### Đầu vào:
```
6
7 2 4 7 3 9
```
#### Đầu ra:
```
2 3 7
```
""",
        "solver": solve_vt09,
        "test_generator": lambda i: (
            f"6\n7 2 4 7 3 9\n" if i == 0 else
            f"5\n4 6 8 9 10\n" if i == 1 else
            f"15\n" + " ".join(str(random.choice([2, 3, 5, 7, 11, 13, 17, 19, 4, 6, 8, 9, 12])) for _ in range(15)) + "\n" if i < 4 else
            f"50\n" + " ".join(str(random.randint(-100, 500)) for _ in range(50)) + "\n" if i < 7 else
            f"2000\n" + " ".join(str(random.randint(-1000, 10000)) for _ in range(2000)) + "\n"
        )
    },
    {
        "code": "maxsum",
        "name": "MAXSUM – Dãy con có tổng lớn nhất",
        "points": 25.0,
        "group": "dp",
        "time_limit": 1.5,
        "memory_limit": 262144,
        "types": ["dynamic-programming"],
        "description": """Cho dãy số nguyên gồm $n$ phần tử $A = [A_1, A_2, \\dots, A_n]$. Dãy số có thể chứa cả các số nguyên âm.

Hãy tìm một đoạn con liên tiếp $A[i \\dots j]$ ($1 \\le i \\le j \\le n$) sao cho tổng các phần tử trong đoạn con này đạt giá trị lớn nhất (Bài toán Kadane).

### Dữ liệu vào
- Dòng đầu tiên chứa số nguyên dương $n$ ($1 \\le n \\le 10^6$).
- Dòng thứ hai chứa $n$ số nguyên $A_1, A_2, \\dots, A_n$ ($-10^9 \\le A_i \\le 10^9$).

### Dữ liệu ra
- In ra một số nguyên duy nhất là tổng lớn nhất của một đoạn con liên tiếp trong dãy.

### Giới hạn
- Subtask 1 (30% số điểm): $n \\le 1000$.
- Subtask 2 (70% số điểm): $n \\le 10^6$.

### Ví dụ
#### Đầu vào:
```
6
-2 3 4 -1 5 -3
```
#### Đầu ra:
```
11
```
*Giải thích:* Đoạn con có tổng lớn nhất là $[3, 4, -1, 5]$ với tổng bằng $3 + 4 + (-1) + 5 = 11$.
""",
        "solver": solve_maxsum,
        "test_generator": lambda i: (
            f"6\n-2 3 4 -1 5 -3\n" if i == 0 else
            f"5\n-5 -2 -9 -1 -8\n" if i == 1 else
            f"10\n" + " ".join(str(random.randint(-20, 20)) for _ in range(10)) + "\n" if i < 4 else
            f"100\n" + " ".join(str(random.randint(-1000, 1000)) for _ in range(100)) + "\n" if i < 7 else
            f"10000\n" + " ".join(str(random.randint(-10**6, 10**6)) for _ in range(10000)) + "\n"
        )
    },
    {
        "code": "twosum",
        "name": "TWOSUM – Hai số có tổng bằng S",
        "points": 25.0,
        "group": "sortsearch",
        "time_limit": 1.0,
        "memory_limit": 262144,
        "types": ["sorting", "binary-search"],
        "description": """Cho mảng $A$ gồm $n$ số nguyên và một số nguyên mục tiêu $S$.

Hãy tìm hai chỉ số $i$ và $j$ ($1 \\le i < j \\le n$) sao cho:
$$A_i + A_j = S$$

Nếu có nhiều cặp chỉ số thỏa mãn, hãy in ra cặp có chỉ số $i$ nhỏ nhất; nếu vẫn có nhiều cặp, chọn cặp có chỉ số $j$ nhỏ nhất. Nếu không tìm thấy cặp nào thỏa mãn, in ra `-1`.

### Dữ liệu vào
- Dòng đầu tiên chứa hai số nguyên $n$ và $S$ ($2 \\le n \\le 10^5, -10^9 \\le S \\le 10^9$).
- Dòng thứ hai chứa $n$ số nguyên $A_1, A_2, \\dots, A_n$ ($-10^9 \\le A_i \\le 10^9$).

### Dữ liệu ra
- In ra hai số nguyên $i$ và $j$ ($1 \\le i < j \\le n$) cách nhau bởi dấu cách, hoặc in ra `-1` nếu không tồn tại.

### Ví dụ
#### Đầu vào:
```
5 9
2 7 11 15 3
```
#### Đầu ra:
```
1 2
```
*Giải thích:* $A_1 + A_2 = 2 + 7 = 9$.
""",
        "solver": solve_twosum,
        "test_generator": lambda i: (
            f"5 9\n2 7 11 15 3\n" if i == 0 else
            f"4 10\n1 2 3 4\n" if i == 1 else
            (lambda: (lambda arr, s: f"10 {s}\n" + " ".join(str(x) for x in arr) + "\n")([random.randint(1, 50) for _ in range(10)], random.randint(10, 80)))() if i < 4 else
            (lambda: (lambda arr, s: f"100 {s}\n" + " ".join(str(x) for x in arr) + "\n")([random.randint(-100, 100) for _ in range(100)], random.randint(-50, 50)))() if i < 7 else
            (lambda: (lambda arr, s: f"5000 {s}\n" + " ".join(str(x) for x in arr) + "\n")([random.randint(-10**6, 10**6) for _ in range(5000)], random.randint(-10**5, 10**5)))()
        )
    },
    {
        "code": "taxi158b",
        "name": "158B – Taxi (Codeforces Greedy)",
        "points": 25.0,
        "group": "sortsearch",
        "time_limit": 1.0,
        "memory_limit": 262144,
        "types": ["sorting", "algorithms"],
        "description": """Sau giờ tan học, $n$ nhóm học sinh quyết định cùng nhau đi taxi về nhà. Nhóm thứ $i$ có $s_i$ học sinh ($1 \\le s_i \\le 4$).

Mỗi chiếc taxi có thể chở tối đa $4$ hành khách. Các bạn trong cùng một nhóm phải đi chung trên một chiếc xe (không được phép tách nhóm). Các nhóm khác nhau có thể ngồi chung xe nếu tổng số người không vượt quá $4$.

Hãy tính số lượng xe taxi tối thiểu cần thuê để chở tất cả các học sinh về nhà.

### Dữ liệu vào
- Dòng đầu tiên chứa số nguyên $n$ ($1 \\le n \\le 10^5$) — số lượng nhóm học sinh.
- Dòng thứ hai chứa $n$ số nguyên $s_1, s_2, \\dots, s_n$ ($1 \\le s_i \\le 4$).

### Dữ liệu ra
- In ra một số nguyên duy nhất — số lượng xe taxi tối thiểu cần thuê.

### Ví dụ
#### Đầu vào:
```
5
1 2 4 3 3
```
#### Đầu ra:
```
4
```
""",
        "solver": solve_taxi158b,
        "test_generator": lambda i: (
            f"5\n1 2 4 3 3\n" if i == 0 else
            f"8\n2 3 4 4 2 1 3 1\n" if i == 1 else
            f"10\n" + " ".join(str(random.randint(1, 4)) for _ in range(10)) + "\n" if i < 4 else
            f"100\n" + " ".join(str(random.randint(1, 4)) for _ in range(100)) + "\n" if i < 7 else
            f"5000\n" + " ".join(str(random.randint(1, 4)) for _ in range(5000)) + "\n"
        )
    }
]

def seed_placement_problems():
    print("--- Seeding Placement Exam Problems ---")
    created_problems = []
    
    for cfg in PROBLEMS_CONFIG:
        code = cfg["code"]
        pdir = PROBLEMS_DIR / code
        pdir.mkdir(parents=True, exist_ok=True)
        
        # Generate 10 test cases: 2 samples, 8 secret
        num_tests = 10
        tc_points = round(cfg["points"] / num_tests, 2)
        test_cases_yml = []
        
        for idx in range(num_tests):
            is_sample = (idx < 2)
            prefix = f"sample_{idx+1:03d}" if is_sample else f"secret_{idx-1:03d}"
            
            in_file = f"{prefix}.in"
            ans_file = f"{prefix}.ans"
            
            in_data = cfg["test_generator"](idx)
            ans_data = cfg["solver"](in_data)
            
            (pdir / in_file).write_text(in_data, encoding="utf-8")
            (pdir / ans_file).write_text(ans_data, encoding="utf-8")
            
            test_cases_yml.append({
                "in": in_file,
                "out": ans_file,
                "points": tc_points
            })
            
        # Write init.yml
        init_content = {
            "archive": None,
            "test_cases": test_cases_yml
        }
        with open(pdir / "init.yml", "w", encoding="utf-8") as f:
            yaml.dump(init_content, f, default_flow_style=False, sort_keys=False)
            
        # Database problem model
        grp = ProblemGroup.objects.filter(name=cfg["group"]).first()
        problem, created = Problem.objects.update_or_create(
            code=code,
            defaults={
                "name": cfg["name"],
                "description": cfg["description"],
                "time_limit": cfg["time_limit"],
                "memory_limit": cfg["memory_limit"],
                "points": cfg["points"],
                "partial": False,
                "is_public": True,
                "group": grp,
                "date": timezone.now(),
            }
        )
        
        # Types
        for t_name in cfg["types"]:
            ptype, _ = ProblemType.objects.get_or_create(name=t_name[:20], defaults={"full_name": t_name})
            problem.types.add(ptype)
            
        print(f"  [Problem] {code:10s} -> '{cfg['name']}' (pts={cfg['points']}, tests={num_tests})")
        created_problems.append(problem)

    return created_problems

def seed_placement_contest(problems):
    print("\n--- Seeding Placement Contest: chuyentin90 ---")
    admin_prof = Profile.objects.filter(user__username='admin').first() or Profile.objects.first()
    
    contest, created = Contest.objects.update_or_create(
        key="chuyentin90",
        defaults={
            "name": "Kiểm Tra Đầu Vào Lớp Chuyên Tin – VCoderLog",
            "description": "Bài thi đánh giá năng lực lập trình và tư duy thuật toán 90 phút dành cho ứng viên lớp Chuyên Tin VCoderLog (MANG, VT09, MAXSUM, TWOSUM).",
            "time_limit": timedelta(minutes=90),
            "start_time": timezone.now() - timedelta(days=30),
            "end_time": timezone.now() + timedelta(days=365),
            "is_visible": True,
            "format_name": "ioi",
            "scoreboard_visibility": Contest.SCOREBOARD_VISIBLE,
        }
    )
    if admin_prof:
        contest.authors.add(admin_prof)
        
    # Clear existing contest problems to avoid duplicate order
    ContestProblem.objects.filter(contest=contest).delete()
    
    # 4 Main problems: mang, vt09, maxsum, twosum
    main_codes = ["mang", "vt09", "maxsum", "twosum"]
    prefix_letters = ["A", "B", "C", "D"]
    
    for idx, code in enumerate(main_codes, 1):
        prob = Problem.objects.get(code=code)
        cp = ContestProblem.objects.create(
            contest=contest,
            problem=prob,
            order=idx,
            points=int(prob.points),
            partial=True
        )
        print(f"  [Contest Problem] #{idx}. {prob.name} ({cp.points} pts)")
        
    print(f"Contest 'chuyentin90' created successfully! Total problems: {contest.problems.count()}")
    return contest

if __name__ == "__main__":
    probs = seed_placement_problems()
    seed_placement_contest(probs)
    print("\nAll placement problems and contest seeded successfully!")
