#!/usr/bin/env python3
"""
Seed contests and problems for Milestone 5 (Screens 4 & 5).
"""
import os
import sys
from pathlib import Path
from datetime import timedelta

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.utils import timezone
from judge.models import Contest, Problem, ContestProblem, ProblemType, ProblemGroup, Language, Judge, ProblemTranslation

now = timezone.now()

# 1. Update/Create monthly2026 (Upcoming Featured Contest)
c_monthly, _ = Contest.objects.get_or_create(
    key='monthly2026',
    defaults={
        'name': 'DMOJ Monthly Contest #5',
        'start_time': now + timedelta(days=2),
        'end_time': now + timedelta(days=2, hours=3),
        'time_limit': timedelta(hours=3),
        'is_rated': True,
        'is_visible': True,
        'summary': 'Our monthly rated contest featuring a mix of algorithmic and data structure problems. Open to everyone!',
    }
)
c_monthly.name = 'DMOJ Monthly Contest #5'
c_monthly.summary = 'Our monthly rated contest featuring a mix of algorithmic and data structure problems. Open to everyone!'
c_monthly.save()

# 2. Update/Create cf965 (Ongoing Contest)
c_cf, _ = Contest.objects.get_or_create(
    key='cf965',
    defaults={
        'name': 'Codeforces Round 965 (Div. 2)',
        'start_time': now - timedelta(hours=1),
        'end_time': now + timedelta(hours=2),
        'time_limit': timedelta(hours=2),
        'is_rated': True,
        'is_visible': True,
        'summary': 'Codeforces Round 965 featured contest with algorithmic challenges.',
    }
)
c_cf.start_time = now - timedelta(hours=1)
c_cf.end_time = now + timedelta(hours=2)
c_cf.is_visible = True
c_cf.save()

# 3. Update/Create wcc2026 (Active/Ongoing World Coding Championship 2026)
c_wcc, _ = Contest.objects.get_or_create(
    key='wcc2026',
    defaults={
        'name': 'World Coding Championship 2026',
        'start_time': now - timedelta(hours=1),
        'end_time': now + timedelta(hours=4),
        'time_limit': timedelta(hours=5),
        'is_rated': True,
        'is_visible': True,
        'summary': 'World Coding Championship 2026 flagship live contest featuring advanced algorithmic and data structure challenges.',
        'description': 'Welcome to the World Coding Championship 2026! Compete against top programmers worldwide in this active contest arena.',
    }
)
c_wcc.name = 'World Coding Championship 2026'
c_wcc.start_time = now - timedelta(hours=1)
c_wcc.end_time = now + timedelta(hours=4)
c_wcc.time_limit = timedelta(hours=5)
c_wcc.is_rated = True
c_wcc.is_visible = True
c_wcc.summary = 'World Coding Championship 2026 flagship live contest featuring advanced algorithmic and data structure challenges.'
c_wcc.description = 'Welcome to the World Coding Championship 2026! Compete against top programmers worldwide in this active contest arena.'
c_wcc.save()

group = ProblemGroup.objects.first()
all_langs = Language.objects.all()

sample_problems = [
    {
        'code': 'array_reconstruction',
        'name': 'Array Reconstruction',
        'points': 100,
        'types': ['math', 'implementation'],
        'description': """You are given an array $b$ of length $n - 1$, which represents the pairwise sums of an unknown array $a$ of length $n$.

Formally, for all $1 \\le i \\le n - 1$, we have:
$$b_i = a_i + a_{i+1}$$

Your task is to reconstruct any valid array $a$ that satisfies the above conditions, or determine that no such array exists.

### Input
The first line contains an integer $n$ ($2 \\le n \\le 2 \\cdot 10^5$) — the length of the array $a$.
The second line contains $n - 1$ integers $b_1, b_2, \\dots, b_{n-1}$ ($-10^9 \\le b_i \\le 10^9$) — the pairwise sums.

### Output
If there exists a valid array $a$, output $n$ integers $a_1, a_2, \\dots, a_n$ such that $a_i + a_{i+1} = b_i$ for all $1 \\le i \\le n - 1$.
If multiple solutions exist, output any of them. If no solution exists, output $-1$.

### Sample Input 1
```
4
3 1 2
```

### Sample Output 1
```
1 2 -1 3
```

### Sample Input 2
```
3
5 5
```

### Sample Output 2
```
2 3 2
```

### Note / Explanation
In Example 1, with reconstructed array $a = [1, 2, -1, 3]$:
- $a_1 + a_2 = 1 + 2 = 3 = b_1$
- $a_2 + a_3 = 2 + (-1) = 1 = b_2$
- $a_3 + a_4 = -1 + 3 = 2 = b_3$
All pairwise sum constraints are satisfied.
""",
        'order': 1,
    },
    {
        'code': 'good_subarrays',
        'name': 'Good Subarrays',
        'points': 100,
        'types': ['dp', 'arrays'],
        'description': """A subarray is defined as **good** if the sum of its elements equals its length.

Given an array of $n$ digits, calculate the number of good contiguous subarrays.

### Input
The first line contains an integer $t$ ($1 \\le t \\le 1000$) — the number of test cases.

The first line of each test case contains an integer $n$ ($1 \\le n \\le 10^5$) — the length of the array.
The second line of each test case contains a string of $n$ decimal digits $a_1 a_2 \\dots a_n$ ($0 \\le a_i \\le 9$).

It is guaranteed that the sum of $n$ over all test cases does not exceed $10^5$.

### Output
For each test case, output a single integer — the number of good contiguous subarrays.

### Sample Input
```
3
3
120
5
11011
6
600005
```

### Sample Output
```
3
6
1
```

### Note / Explanation
- In the first test case ($120$), the good subarrays are:
  - $a[1..1] = [1]$ (length 1, sum 1)
  - $a[2..3] = [2, 0]$ (length 2, sum 2)
  - $a[1..3] = [1, 2, 0]$ (length 3, sum 3)
- In the second test case ($11011$), there are 6 good subarrays.
- In the third test case ($600005$), the only good subarray is $a[2..6] = [0, 0, 0, 0, 5]$ (length 5, sum 5).
""",
        'order': 2,
    },
    {
        'code': 'tree_queries',
        'name': 'Tree Queries',
        'points': 200,
        'types': ['trees', 'graphs'],
        'description': """You are given a rooted tree consisting of $n$ vertices numbered from $1$ to $n$. The root of the tree is vertex $1$.

You are given $m$ queries. For each query, you are given a set of $k$ vertices $v_1, v_2, \\dots, v_k$. You need to determine if there exists a path starting at the root (vertex $1$) such that every given vertex in the query lies on the path or is adjacent to a vertex on the path (distance $\\le 1$ to the path).

### Input
The first line contains two integers $n$ and $m$ ($2 \\le n \\le 2 \\cdot 10^5$, $1 \\le m \\le 2 \\cdot 10^5$) — the number of vertices and the number of queries.

The next $n - 1$ lines describe the edges of the tree. Each line contains two integers $u$ and $v$ ($1 \\le u, v \\le n, u \\ne v$).

The next $m$ lines describe the queries. Each query begins with an integer $k_i$ ($1 \\le k_i \\le n$), followed by $k_i$ integers $v_1, v_2, \\dots, v_{k_i}$ — the vertices for the $i$-th query.

### Output
For each query, print `YES` if such a path from root exists, or `NO` otherwise.

### Sample Input
```
10 3
1 2
2 3
3 4
2 5
5 6
1 7
7 8
8 9
9 10
3 4 5 6
2 5 8
2 3 6
```

### Sample Output
```
YES
NO
YES
```
""",
        'order': 3,
    },
]

for sp in sample_problems:
    p, created = Problem.objects.get_or_create(
        code=sp['code'],
        defaults={
            'name': sp['name'],
            'description': sp['description'],
            'points': sp['points'],
            'time_limit': 2.0,
            'memory_limit': 262144,
            'is_public': True,
            'group': group,
        }
    )
    if not created:
        p.name = sp['name']
        p.description = sp['description']
        p.points = sp['points']
        p.save()
    p.allowed_languages.set(all_langs)
    for t_name in sp['types']:
        pt, _ = ProblemType.objects.get_or_create(name=t_name)
        p.types.add(pt)

    # Seed Vietnamese translation
    sample_translations = {
        'good_subarrays': {
            'name': 'Mảng Con Tốt (Good Subarrays)',
            'description': """Một mảng con được định nghĩa là **tốt** nếu tổng các phần tử của nó bằng chính độ dài của nó.

Cho một mảng gồm $n$ chữ số, hãy đếm số lượng mảng con liên tiếp tốt.

### Dữ liệu vào
Dòng đầu tiên chứa số nguyên $t$ ($1 \\le t \\le 1000$) — số lượng bộ test.

Dòng đầu tiên của mỗi bộ test chứa số nguyên $n$ ($1 \\le n \\le 10^5$) — độ dài của mảng.
Dòng thứ hai của mỗi bộ test chứa một chuỗi gồm $n$ chữ số thập phân $a_1 a_2 \\dots a_n$ ($0 \\le a_i \\le 9$).

Đảm bảo rằng tổng của $n$ trên tất cả các bộ test không vượt quá $10^5$.

### Dữ liệu ra
Với mỗi bộ test, in ra một số nguyên duy nhất — số lượng mảng con liên tiếp tốt.

### Ví dụ đầu vào
```
3
3
120
5
11011
6
600005
```

### Ví dụ đầu ra
```
3
6
1
```

### Giải thích
- Trong bộ test đầu tiên ($120$), các mảng con tốt là:
  - $a[1..1] = [1]$ (độ dài 1, tổng 1)
  - $a[2..3] = [2, 0]$ (độ dài 2, tổng 2)
  - $a[1..3] = [1, 2, 0]$ (độ dài 3, tổng 3)
- Trong bộ test thứ hai ($11011$), có tất cả 6 mảng con tốt.
- Trong bộ test thứ ba ($600005$), mảng con tốt duy nhất là $a[2..6] = [0, 0, 0, 0, 5]$ (độ dài 5, tổng 5).
"""
        },
        'array_reconstruction': {
            'name': 'Khôi Phục Mảng (Array Reconstruction)',
            'description': """Cho một mảng $b$ có độ dài $n - 1$, đại diện cho tổng các cặp phần tử liền kề của một mảng $a$ chưa biết có độ dài $n$.

Cụ thể, với mọi $1 \\le i \\le n - 1$:
$$b_i = a_i + a_{i+1}$$

Nhiệm vụ của bạn là khôi phục một mảng $a$ hợp lệ bất kỳ thỏa mãn các điều kiện trên, hoặc xác định rằng không tồn tại mảng nào như vậy.

### Dữ liệu vào
Dòng đầu tiên chứa số nguyên $n$ ($2 \\le n \\le 2 \\cdot 10^5$) — độ dài của mảng $a$.
Dòng thứ hai chứa $n - 1$ số nguyên $b_1, b_2, \\dots, b_{n-1}$ ($-10^9 \\le b_i \\le 10^9$) — các tổng từng cặp.

### Dữ liệu ra
Nếu tồn tại mảng $a$ hợp lệ, in ra $n$ số nguyên $a_1, a_2, \\dots, a_n$ sao cho $a_i + a_{i+1} = b_i$ với mọi $1 \\le i \\le n - 1$.
Nếu có nhiều nghiệm, in ra bất kỳ nghiệm nào. Nếu không tồn tại nghiệm, in ra $-1$.

### Ví dụ đầu vào 1
```
4
3 1 2
```

### Ví dụ đầu ra 1
```
1 2 -1 3
```

### Ví dụ đầu vào 2
```
3
5 5
```

### Ví dụ đầu ra 2
```
2 3 2
```

### Giải thích
Trong Ví dụ 1, với mảng khôi phục $a = [1, 2, -1, 3]$:
- $a_1 + a_2 = 1 + 2 = 3 = b_1$
- $a_2 + a_3 = 2 + (-1) = 1 = b_2$
- $a_3 + a_4 = -1 + 3 = 2 = b_3$
Tất cả các điều kiện tổng từng cặp đều được thỏa mãn.
"""
        },
        'tree_queries': {
            'name': 'Truy Vấn Trên Cây (Tree Queries)',
            'description': """Cho một cây có gốc gồm $n$ đỉnh được đánh số từ $1$ đến $n$. Gốc của cây là đỉnh $1$.

Có $m$ truy vấn. Với mỗi truy vấn, bạn được cho một tập gồm $k$ đỉnh $v_1, v_2, \\dots, v_k$. Bạn cần xác định xem có tồn tại một đường đi xuất phát từ gốc (đỉnh $1$) sao cho mọi đỉnh được cho trong truy vấn đều nằm trên đường đi hoặc kề với một đỉnh trên đường đi (khoảng cách $\\le 1$ tới đường đi) hay không.

### Dữ liệu vào
Dòng đầu tiên chứa hai số nguyên $n$ và $m$ ($2 \\le n \\le 2 \\cdot 10^5$, $1 \\le m \\le 2 \\cdot 10^5$) — số đỉnh và số lượng truy vấn.
$n - 1$ dòng tiếp theo mô tả các cạnh của cây. Mỗi dòng chứa hai số nguyên $u$ và $v$ ($1 \\le u, v \\le n, u \\ne v$).
$m$ dòng tiếp theo mô tả các truy vấn. Mỗi truy vấn bắt đầu bằng số nguyên $k_i$ ($1 \\le k_i \\le n$), theo sau là $k_i$ số nguyên $v_1, v_2, \\dots, v_{k_i}$ — danh sách các đỉnh của truy vấn thứ $i$.

### Dữ liệu ra
Với mỗi truy vấn, in ra `YES` nếu tồn tại đường đi thỏa mãn từ gốc, hoặc `NO` nếu ngược lại.

### Ví dụ đầu vào
```
10 3
1 2
2 3
3 4
2 5
5 6
1 7
7 8
8 9
9 10
3 4 5 6
2 5 8
2 3 6
```

### Ví dụ đầu ra
```
YES
NO
YES
```
"""
        }
    }
    if sp['code'] in sample_translations:
        st = sample_translations[sp['code']]
        pt, _ = ProblemTranslation.objects.get_or_create(problem=p, language='vi')
        pt.name = st['name']
        pt.description = st['description']
        pt.save()

    # Link problem to judges so usable_languages is populated
    for j in Judge.objects.all():
        j.problems.add(p)

    for c_obj in (c_monthly, c_wcc):
        cp, _ = ContestProblem.objects.get_or_create(
            contest=c_obj,
            problem=p,
            defaults={'points': sp['points'], 'order': sp['order'], 'output_prefix_override': 0}
        )
        cp.order = sp['order']
        cp.points = sp['points']
        cp.save()

# Also link aplusb to ongoing contest cf965, monthly2026, and wcc2026
p_aplusb = Problem.objects.filter(code='aplusb').first()
if p_aplusb:
    pt, _ = ProblemTranslation.objects.get_or_create(problem=p_aplusb, language='vi')
    pt.name = 'A Cộng B (A Plus B)'
    pt.description = """Cho hai số nguyên $A$ và $B$. Hãy tính tổng của chúng.

### Dữ liệu vào
Hai số nguyên $A$ và $B$ cách nhau bởi dấu cách ($-10^9 \\le A, B \\le 10^9$).

### Dữ liệu ra
In ra một số nguyên duy nhất là tổng $A + B$.

### Ví dụ đầu vào
```
1 2
```

### Ví dụ đầu ra
```
3
```
"""
    pt.save()

    ContestProblem.objects.get_or_create(contest=c_cf, problem=p_aplusb, defaults={'points': 100, 'order': 1, 'output_prefix_override': 0})
    for c_obj in (c_monthly, c_wcc):
        cp_aplusb, _ = ContestProblem.objects.get_or_create(contest=c_obj, problem=p_aplusb, defaults={'points': 50, 'order': 4, 'output_prefix_override': 0})
        cp_aplusb.order = 4
        cp_aplusb.save()
    for j in Judge.objects.all():
        j.problems.add(p_aplusb)

print("Seed complete! Contests and problems successfully initialized with clear examples and judge linkages.")

