#!/usr/bin/env python3
"""
scripts/seed_interleaved_problems.py
Generates 1,200 diverse, interleaved competitive programming problems for VCoder Arena.
- Problem codes: p0001 to p1200
- 12 Algorithmic Domains interleaved round-robin
- 102 distinct algorithmic solvers & archetypes
- No two adjacent problems share the same domain or solution algorithm
- 100% natural, creative Vietnamese titles & stories
"""

import os
import sys
import yaml
import shutil
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.utils import timezone
from judge.models import Problem, ProblemGroup, ProblemType, Language, Judge
from scripts.problem_titles_bank import get_title, get_story_description
from scripts.archetype_definitions import get_domain_archetypes

# Base directory for problem test data
REMOTE_PROBLEMS_DIR = Path("/home/tdao7/dmoj-judge/problems")
LOCAL_PROBLEMS_DIR = JUDGE_ROOT.parent / "problems"
PROBLEMS_DIR = REMOTE_PROBLEMS_DIR if REMOTE_PROBLEMS_DIR.exists() else LOCAL_PROBLEMS_DIR
PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)

print(f"Using Problem Data Root: {PROBLEMS_DIR}")

# 12 Algorithmic Domains metadata
DOMAINS = {
    "cb": {
        "group_id": "basic",
        "group_name": "Cơ bản & Nhập xuất",
        "types": ["basic-io", "math", "implementation"],
        "time_limit": 1.0,
    },
    "dp": {
        "group_id": "dp",
        "group_name": "Quy hoạch động",
        "types": ["dp", "algorithms"],
        "time_limit": 2.0,
    },
    "str": {
        "group_id": "string",
        "group_name": "Xử lý chuỗi ký tự",
        "types": ["strings", "implementation"],
        "time_limit": 1.0,
    },
    "gr": {
        "group_id": "graph",
        "group_name": "Đồ thị & Cây",
        "types": ["graphs", "trees"],
        "time_limit": 2.0,
    },
    "dk": {
        "group_id": "condition",
        "group_name": "Cấu trúc rẽ nhánh",
        "types": ["implementation", "math"],
        "time_limit": 1.0,
    },
    "mth": {
        "group_id": "number",
        "group_name": "Số học & Toán rời rạc",
        "types": ["math", "number-theory"],
        "time_limit": 1.5,
    },
    "ds": {
        "group_id": "ds",
        "group_name": "Cấu trúc dữ liệu",
        "types": ["data-structures", "trees"],
        "time_limit": 2.0,
    },
    "vt": {
        "group_id": "array1d",
        "group_name": "Mảng một chiều",
        "types": ["arrays", "implementation"],
        "time_limit": 1.0,
    },
    "vl": {
        "group_id": "loop",
        "group_name": "Vòng lặp & Dãy số",
        "types": ["implementation", "math"],
        "time_limit": 1.0,
    },
    "srt": {
        "group_id": "sortsearch",
        "group_name": "Sắp xếp & Tìm kiếm",
        "types": ["binary-search", "arrays"],
        "time_limit": 1.5,
    },
    "mt": {
        "group_id": "matrix",
        "group_name": "Mảng hai chiều",
        "types": ["arrays", "implementation", "math"],
        "time_limit": 1.5,
    },
    "fnc": {
        "group_id": "recursion",
        "group_name": "Hàm & Đệ quy",
        "types": ["recursion", "implementation"],
        "time_limit": 1.5,
    }
}

# The interleaved order of domains
DOMAINS_ORDER = ["cb", "dp", "str", "gr", "dk", "mth", "ds", "vt", "vl", "srt", "mt", "fnc"]

def seed_interleaved_problems():
    print("=================================================================")
    print("Starting 1,200 Interleaved Diverse Problem Bank Generation...")
    print("=================================================================")

    all_languages = list(Language.objects.all())
    judges = list(Judge.objects.all())
    print(f"Detected {len(all_languages)} programming languages and {len(judges)} judge daemon(s).")

    # 1. Ensure Groups and Types exist
    group_map = {}
    type_map = {}
    for prefix, dom in DOMAINS.items():
        grp, _ = ProblemGroup.objects.get_or_create(
            name=dom["group_id"],
            defaults={"full_name": dom["group_name"]}
        )
        group_map[prefix] = grp
        for t in dom["types"]:
            pt, _ = ProblemType.objects.get_or_create(
                name=t,
                defaults={"full_name": t.replace("-", " ").title()}
            )
            type_map[t] = pt

    # 2. Clean up previous old codes (cb001..ds100) if any
    old_deleted, _ = Problem.objects.filter(code__regex=r"^(cb|dk|vl|vt|mt|str|fnc|srt|mth|dp|gr|ds)[0-9]+").delete()
    if old_deleted > 0:
        print(f"Cleaned up {old_deleted} old grouped placeholder problems from DB.")

    # 3. Generate 1,200 interleaved problems
    # 100 rounds * 12 domains = 1,200 problems
    total_created = 0
    total_updated = 0

    p_num = 0
    for r in range(1, 101): # 1 to 100
        for dom_prefix in DOMAINS_ORDER:
            p_num += 1
            code = f"p{p_num:04d}"
            dom = DOMAINS[dom_prefix]
            grp = group_map[dom_prefix]

            title = get_title(dom_prefix, r)
            story = get_story_description(dom_prefix, r, title)
            archetypes = get_domain_archetypes(dom_prefix)
            arch = archetypes[(r - 1) % len(archetypes)]

            pts = arch["pts"] + (r % 5) * 2
            testcases = arch["tests"]

            sample_in = testcases[0][0]
            sample_out = testcases[0][1]

            description = f"""### Đề bài
{story}

### Đầu vào
- {arch['input_desc']}

### Đầu ra
- {arch['output_desc']}

### Giới hạn & Ràng buộc
- Thời gian chạy tối đa: **{dom['time_limit']} giây**.
- Bộ nhớ tối đa: **256 MB**.
- {arch['constraints']}

### Ví dụ mẫu
#### Đầu vào
```
{sample_in}
```

#### Đầu ra
```
{sample_out.strip()}
```
"""

            # Create or update Problem
            problem, created = Problem.objects.get_or_create(
                code=code,
                defaults={
                    "name": title,
                    "description": description,
                    "points": pts,
                    "time_limit": dom["time_limit"],
                    "memory_limit": 262144,
                    "is_public": True,
                    "group": grp,
                    "date": timezone.now(),
                }
            )

            if not created:
                problem.name = title
                problem.description = description
                problem.points = pts
                problem.time_limit = dom["time_limit"]
                problem.memory_limit = 262144
                problem.group = grp
                problem.is_public = True
                problem.save()
                total_updated += 1
            else:
                total_created += 1

            # Bind languages and types
            problem.allowed_languages.set(all_languages)
            for t_name in dom["types"]:
                problem.types.add(type_map[t_name])

            # Bind judges
            for j in judges:
                j.problems.add(problem)

            # Generate Testcase Files
            prob_dir = PROBLEMS_DIR / code
            prob_dir.mkdir(parents=True, exist_ok=True)

            yaml_test_cases = []
            # Samples (first 2)
            for s_idx in range(min(2, len(testcases))):
                in_name = f"sample_{s_idx+1:03d}.in"
                ans_name = f"sample_{s_idx+1:03d}.ans"
                with open(prob_dir / in_name, "w") as f_in:
                    f_in.write(testcases[s_idx][0].strip() + "\n")
                with open(prob_dir / ans_name, "w") as f_ans:
                    f_ans.write(testcases[s_idx][1].strip() + "\n")
                yaml_test_cases.append({
                    "in": in_name,
                    "out": ans_name,
                    "points": round(pts / len(testcases), 1)
                })

            # Secrets (remaining)
            for sc_idx in range(2, len(testcases)):
                in_name = f"secret_{sc_idx-1:03d}.in"
                ans_name = f"secret_{sc_idx-1:03d}.ans"
                with open(prob_dir / in_name, "w") as f_in:
                    f_in.write(testcases[sc_idx][0].strip() + "\n")
                with open(prob_dir / ans_name, "w") as f_ans:
                    f_ans.write(testcases[sc_idx][1].strip() + "\n")
                yaml_test_cases.append({
                    "in": in_name,
                    "out": ans_name,
                    "points": round(pts / len(testcases), 1)
                })

            init_yaml_data = {
                "archive": None,
                "test_cases": yaml_test_cases
            }
            with open(prob_dir / "init.yml", "w") as f_yml:
                f_yml.write("# Generated by VCoder Arena Interleaved Problem Bank Generator\n")
                yaml.dump(init_yaml_data, f_yml, default_flow_style=False)

        if r % 10 == 0:
            print(f"Progress: Round {r}/100 completed ({p_num}/1200 problems generated)...")

    print("\n" + "=" * 65)
    print(f"SUCCESS! Interleaved Seeding Complete:")
    print(f"  - Total New Problems Created: {total_created}")
    print(f"  - Total Problems Updated: {total_updated}")
    print(f"  - Total Problem Count in DB: {Problem.objects.count()}")
    print("=================================================================")

if __name__ == "__main__":
    seed_interleaved_problems()
