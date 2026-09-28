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
from judge.models import Contest, Problem, ContestProblem, ProblemType, ProblemGroup, Language

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

### Examples

#### Example 1
```
4
3 1 2
```
```
1 2 -1 3
```
""",
        'order': 1,
    },
    {
        'code': 'good_subarrays',
        'name': 'Good Subarrays',
        'points': 100,
        'types': ['dp', 'arrays'],
        'description': """A subarray is defined as good if the sum of its elements equals its length.

Given an array of $n$ digits, calculate the number of good contiguous subarrays.

### Input
The first line contains an integer $t$ — the number of test cases.
Each test case contains $n$ and the string of digits.

### Output
For each test case, output the number of good subarrays.
""",
        'order': 2,
    },
    {
        'code': 'tree_queries',
        'name': 'Tree Queries',
        'points': 200,
        'types': ['trees', 'graphs'],
        'description': """You are given a tree consisting of $n$ vertices rooted at vertex $1$.
Answer $m$ queries regarding paths and subtree properties.
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

    cp, _ = ContestProblem.objects.get_or_create(
        contest=c_monthly,
        problem=p,
        defaults={'points': sp['points'], 'order': sp['order'], 'output_prefix_override': 0}
    )
    cp.order = sp['order']
    cp.points = sp['points']
    cp.save()

# Also link aplusb to ongoing contest cf965
p_aplusb = Problem.objects.filter(code='aplusb').first()
if p_aplusb:
    ContestProblem.objects.get_or_create(contest=c_cf, problem=p_aplusb, defaults={'points': 100, 'order': 1, 'output_prefix_override': 0})

print("Seed complete! Contests and problems successfully initialized.")
