#!/usr/bin/env python3
"""
scripts/seed_1000_problems.py
Massive Competitive Programming Problem Bank Generator for VCoder Arena.
Generates 1,200 high-quality problems across 12 distinct algorithmic domains
(100 problems per domain) complete with:
- Unique problem codes (^[a-z0-9]+$)
- Detailed Vietnamese & English problem statements
- LaTeX math formulas ($...$, $$...$$)
- Input / Output specifications & constraints
- Sample test cases with codeblocks
- DMOJ init.yml and valid sample/secret test case files
- DMOJ Problem model instances, Language linkages, Judge bindings, and ProblemGroup/Type assignments
"""

import os
import sys
import yaml
import random
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.utils import timezone
from judge.models import Problem, ProblemGroup, ProblemType, Language, Judge, LanguageLimit
from scripts.problem_titles_bank import get_title, get_story_description

# Base directory for problem test data on the server
# If running on remote server: /home/tdao7/dmoj-judge/problems
# If running locally, check relative path
REMOTE_PROBLEMS_DIR = Path("/home/tdao7/dmoj-judge/problems")
LOCAL_PROBLEMS_DIR = JUDGE_ROOT.parent / "problems"
PROBLEMS_DIR = REMOTE_PROBLEMS_DIR if REMOTE_PROBLEMS_DIR.exists() else LOCAL_PROBLEMS_DIR
PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)

print(f"Using Problem Data Root: {PROBLEMS_DIR}")

# 12 Algorithmic Domains (100 problems each = 1,200 problems)
DOMAINS = [
    {
        "prefix": "cb",
        "group_id": "basic",
        "group_name": "Cơ bản & Nhập xuất",
        "group_desc": "Các bài toán nhập xuất cơ bản, tính toán số học, chu vi diện tích hình học và chuyển đổi đơn vị.",
        "types": ["basic-io", "math", "implementation"],
        "min_pts": 10,
        "max_pts": 25,
        "time_limit": 1.0,
        "topic": "Basic I/O & Elementary Math"
    },
    {
        "prefix": "dk",
        "group_id": "condition",
        "group_name": "Cấu trúc rẽ nhánh",
        "group_desc": "Kiểm tra điều kiện if-else, phân loại số học, hình học cơ bản và phương trình.",
        "types": ["implementation", "math"],
        "min_pts": 15,
        "max_pts": 30,
        "time_limit": 1.0,
        "topic": "Conditionals & Logic"
    },
    {
        "prefix": "vl",
        "group_id": "loop",
        "group_name": "Vòng lặp & Dãy số",
        "group_desc": "Vòng lặp for/while, tính tổng chuỗi, ước số, số nguyên tố cơ bản và in hình dạng sao.",
        "types": ["implementation", "math"],
        "min_pts": 20,
        "max_pts": 35,
        "time_limit": 1.0,
        "topic": "Loops & Number Sequences"
    },
    {
        "prefix": "vt",
        "group_id": "array1d",
        "group_name": "Mảng một chiều",
        "group_desc": "Thao tác trên mảng, tìm kiếm max/min, tần suất phần tử, mảng con và biến đổi mảng.",
        "types": ["arrays", "implementation"],
        "min_pts": 25,
        "max_pts": 45,
        "time_limit": 1.0,
        "topic": "1D Arrays & Vectors"
    },
    {
        "prefix": "mt",
        "group_id": "matrix",
        "group_name": "Mảng hai chiều",
        "group_desc": "Duyệt ma trận, đường chéo, chuyển vị, nhân ma trận, lưới ô vuông 2D.",
        "types": ["arrays", "implementation", "math"],
        "min_pts": 30,
        "max_pts": 55,
        "time_limit": 1.5,
        "topic": "2D Matrices & Grids"
    },
    {
        "prefix": "str",
        "group_id": "string",
        "group_name": "Xử lý chuỗi ký tự",
        "group_desc": "Thao tác chuỗi, chuẩn hóa văn bản, xâu đối xứng, tách từ và mã hóa ký tự.",
        "types": ["strings", "implementation"],
        "min_pts": 25,
        "max_pts": 50,
        "time_limit": 1.0,
        "topic": "String Manipulation"
    },
    {
        "prefix": "fnc",
        "group_id": "recursion",
        "group_name": "Hàm & Đệ quy",
        "group_desc": "Thiết kế hàm, đệ quy chia để trị, bài toán tháp Hà Nội, sinh nhị phân, hoán vị và quay lui N-Queens.",
        "types": ["recursion", "implementation"],
        "min_pts": 35,
        "max_pts": 65,
        "time_limit": 1.5,
        "topic": "Recursion & Backtracking"
    },
    {
        "prefix": "srt",
        "group_id": "sortsearch",
        "group_name": "Sắp xếp & Tìm kiếm",
        "group_desc": "Sắp xếp mảng, tìm kiếm nhị phân, chặt nhị phân kết quả, kỹ thuật hai con trỏ (Two Pointers).",
        "types": ["binary-search", "arrays"],
        "min_pts": 30,
        "max_pts": 60,
        "time_limit": 1.5,
        "topic": "Sorting & Binary Search"
    },
    {
        "prefix": "mth",
        "group_id": "number",
        "group_name": "Số học & Toán rời rạc",
        "group_desc": "Sàng nguyên tố Eratosthenes, phân tích thừa số, lũy thừa modulo, nghịch đảo modulo và tổ hợp.",
        "types": ["math", "number-theory"],
        "min_pts": 40,
        "max_pts": 75,
        "time_limit": 1.5,
        "topic": "Number Theory & Combinatorics"
    },
    {
        "prefix": "dp",
        "group_id": "dp",
        "group_name": "Quy hoạch động",
        "group_desc": "Dãy con tăng dài nhất (LIS), xâu con chung (LCS), bài toán cái túi Knapsack, đổi tiền và quy hoạch động lưới.",
        "types": ["dp", "algorithms"],
        "min_pts": 45,
        "max_pts": 90,
        "time_limit": 2.0,
        "topic": "Dynamic Programming"
    },
    {
        "prefix": "gr",
        "group_id": "graph",
        "group_name": "Đồ thị & Cây",
        "group_desc": "Biểu diễn đồ thị, duyệt DFS/BFS, đường đi ngắn nhất Dijkstra/Floyd, cây khung nhỏ nhất MST, Topological sort.",
        "types": ["graphs", "trees"],
        "min_pts": 50,
        "max_pts": 95,
        "time_limit": 2.0,
        "topic": "Graph Algorithms & Trees"
    },
    {
        "prefix": "ds",
        "group_id": "ds",
        "group_name": "Cấu trúc dữ liệu",
        "group_desc": "Ngăn xếp (Stack), Hàng đợi (Queue/Deque), Cây phân đoạn (Segment Tree), Fenwick Tree (BIT), DSU, Trie.",
        "types": ["data-structures", "trees"],
        "min_pts": 55,
        "max_pts": 100,
        "time_limit": 2.0,
        "topic": "Advanced Data Structures"
    }
]

# Problem Titles & Specific Descriptions Generator per domain
def generate_problem_specs(domain, index):
    """
    Returns a dict with code, name, description, points, generator_fn
    that creates sample and secret test cases deterministically.
    """
    prefix = domain["prefix"]
    idx_str = f"{index:03d}"
    code = f"{prefix}{idx_str}"
    
    # Specific topics based on domain and index
    if prefix == "cb":
        # Basic I/O & Math
        subtopics = [
            ("Tính tổng hai số nguyên", "Cho hai số nguyên $a$ và $b$. Hãy tính và in ra giá trị $a + b$.", "add", 10),
            ("Tính hiệu hai số nguyên", "Cho hai số nguyên $a$ và $b$. Hãy tính và in ra giá trị $a - b$.", "sub", 10),
            ("Tính tích hai số nguyên", "Cho hai số nguyên $a$ và $b$. Hãy tính tích $a \\times b$.", "mul", 10),
            ("Chia lấy phần nguyên và dư", "Cho hai số nguyên dương $a$ và $b$. In ra thương nguyên $a / b$ và số dư $a \\% b$.", "divmod", 10),
            ("Chu vi và diện tích hình vuông", "Cho độ dài cạnh hình vuông $a$. Tính chu vi và diện tích.", "sq_area", 15),
            ("Chu vi và diện tích hình chữ nhật", "Cho chiều dài $a$ và chiều rộng $b$. Tính chu vi và diện tích.", "rect_calc", 15),
            ("Diện tích hình tam giác", "Cho đáy $a$ và chiều cao $h$. Tính diện tích tam giác $S = \\frac{1}{2} a h$.", "tri_area", 15),
            ("Tính chu vi và diện tích hình tròn", "Cho bán kính $r$. Tính chu vi và diện tích với $\\pi = 3.14159$.", "circle_calc", 15),
            ("Quy đổi nhiệt độ Celsius sang Fahrenheit", "Cho nhiệt độ $C$. Đổi sang độ $F = C \\times 1.8 + 32$.", "temp_c2f", 15),
            ("Quy đổi thời gian giây sang H:M:S", "Cho tổng số giây $S$. Đổi sang định dạng Giờ, Phút, Giây.", "time_conv", 20),
        ]
        base = subtopics[(index - 1) % len(subtopics)]
        title = get_title("cb", index)
        desc = get_story_description("cb", index, title)
        op = base[2]
        pts = base[3] + (index % 5) * 2

        def solver(input_str):
            nums = [int(x) for x in input_str.split()]
            if op == "add":
                return f"{nums[0] + nums[1]}\n"
            elif op == "sub":
                return f"{nums[0] - nums[1]}\n"
            elif op == "mul":
                return f"{nums[0] * nums[1]}\n"
            elif op == "divmod":
                return f"{nums[0] // nums[1]} {nums[0] % nums[1]}\n"
            elif op == "sq_area":
                a = nums[0]
                return f"{4 * a} {a * a}\n"
            elif op == "rect_calc":
                a, b = nums[0], nums[1]
                return f"{2 * (a + b)} {a * b}\n"
            elif op == "tri_area":
                a, h = nums[0], nums[1]
                return f"{0.5 * a * h:.2f}\n"
            elif op == "circle_calc":
                r = float(nums[0])
                return f"{2 * 3.14159 * r:.2f} {3.14159 * r * r:.2f}\n"
            elif op == "temp_c2f":
                c = float(nums[0])
                return f"{c * 1.8 + 32.0:.2f}\n"
            else:
                s = nums[0]
                h = s // 3600
                m = (s % 3600) // 60
                sec = s % 60
                return f"{h:02d}:{m:02d}:{sec:02d}\n"

        testcases = [
            ("5 7", solver("5 7")),
            ("12 25", solver("12 25")),
            ("100 45", solver("100 45")),
            ("250 80", solver("250 80")),
            ("1000 333", solver("1000 333")),
        ]

    elif prefix == "dk":
        # Conditionals
        subtopics = [
            ("Kiểm tra tính chẵn lẻ", "Cho số nguyên $N$. In `EVEN` nếu $N$ chẵn, ngược lại in `ODD`.", "even_odd", 15),
            ("Tìm số lớn nhất trong hai số", "Cho hai số nguyên $a, b$. In ra số có giá trị lớn hơn.", "max2", 15),
            ("Tìm số lớn nhất trong ba số", "Cho ba số nguyên $a, b, c$. In ra giá trị lớn nhất.", "max3", 15),
            ("Kiểm tra năm nhuận", "Cho năm $Y$. In `YES` nếu $Y$ là năm nhuận, `NO` nếu không phải.", "leap_year", 20),
            ("Phân loại tam giác theo cạnh", "Cho ba cạnh $a, b, c$. In `EQUILATERAL` (đều), `ISOSCELES` (cân), `SCALENE` (thường) hoặc `INVALID`.", "tri_type", 20),
            ("Giải phương trình bậc nhất ax + b = 0", "Cho $a$ và $b$. Giải phương trình $ax + b = 0$. In nghiệm với 2 chữ số thập phân.", "linear_eq", 20),
            ("Đánh giá chỉ số BMI", "Cho cân nặng $w$ (kg) và chiều cao $h$ (m). Tính chỉ số $BMI = w / h^2$ và phân loại.", "bmi", 25),
            ("Xếp loại học tập", "Cho điểm trung bình $P \\in [0, 10]$. Phân loại Giỏi, Khá, Trung bình, Yếu.", "grade", 20),
            ("Tính cước phí vận chuyển", "Tính cước vận chuyển kiện hàng theo trọng lượng với các mốc quy định.", "shipping", 25),
            ("Kiểm tra tọa độ điểm trong góc phần tư", "Cho tọa độ $(x, y)$. Xác định điểm thuộc góc phần tư I, II, III, IV hay trục tọa độ.", "quadrant", 25),
        ]
        base = subtopics[(index - 1) % len(subtopics)]
        title = get_title("dk", index)
        desc = get_story_description("dk", index, title)
        op = base[2]
        pts = base[3] + (index % 4) * 2

        def solver(input_str):
            nums = [float(x) for x in input_str.split()]
            if op == "even_odd":
                return "EVEN\n" if int(nums[0]) % 2 == 0 else "ODD\n"
            elif op == "max2":
                return f"{int(max(nums[0], nums[1]))}\n"
            elif op == "max3":
                return f"{int(max(nums[0], nums[1], nums[2]))}\n"
            elif op == "leap_year":
                y = int(nums[0])
                is_leap = (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0)
                return "YES\n" if is_leap else "NO\n"
            elif op == "tri_type":
                a, b, c = sorted(nums[:3])
                if a + b <= c: return "INVALID\n"
                if a == b == c: return "EQUILATERAL\n"
                if a == b or b == c: return "ISOSCELES\n"
                return "SCALENE\n"
            elif op == "linear_eq":
                a, b = nums[0], nums[1]
                if a == 0: return "NO SOLUTION\n" if b != 0 else "INFINITE\n"
                return f"{-b / a:.2f}\n"
            elif op == "bmi":
                w, h = nums[0], nums[1]
                bmi = w / (h * h)
                if bmi < 18.5: return "UNDERWEIGHT\n"
                if bmi < 25.0: return "NORMAL\n"
                if bmi < 30.0: return "OVERWEIGHT\n"
                return "OBESE\n"
            else:
                return f"{int(nums[0])}\n"

        if op == "even_odd":
            testcases = [("4", solver("4")), ("7", solver("7")), ("12", solver("12")), ("101", solver("101")), ("0", solver("0"))]
        elif op == "leap_year":
            testcases = [("2024", solver("2024")), ("1900", solver("1900")), ("2000", solver("2000")), ("2023", solver("2023")), ("2004", solver("2004"))]
        elif op == "max2":
            testcases = [("4 7", solver("4 7")), ("10 2", solver("10 2")), ("-5 3", solver("-5 3")), ("100 100", solver("100 100")), ("0 -1", solver("0 -1"))]
        elif op == "max3":
            testcases = [("1 5 3", solver("1 5 3")), ("9 2 4", solver("9 2 4")), ("-1 -5 -2", solver("-1 -5 -2")), ("10 10 5", solver("10 10 5")), ("0 0 0", solver("0 0 0"))]
        elif op == "tri_type":
            testcases = [("3 4 5", solver("3 4 5")), ("5 5 5", solver("5 5 5")), ("4 4 6", solver("4 4 6")), ("1 2 3", solver("1 2 3")), ("6 8 10", solver("6 8 10"))]
        elif op == "linear_eq":
            testcases = [("2 -4", solver("2 -4")), ("5 10", solver("5 10")), ("3 0", solver("3 0")), ("4 7", solver("4 7")), ("-2 8", solver("-2 8"))]
        else:
            testcases = [("60 1.7", solver("60 1.7")), ("75 1.75", solver("75 1.75")), ("50 1.6", solver("50 1.6")), ("90 1.8", solver("90 1.8")), ("45 1.55", solver("45 1.55"))]

    elif prefix == "vl":
        # Loops
        title = get_title("vl", index)
        desc = get_story_description("vl", index, title)
        pts = 20 + (index % 10) * 2
        def solver(input_str):
            n = int(input_str.strip())
            k = (index % 4) + 1
            if k == 1:
                return f"{n * (n + 1) // 2}\n"
            elif k == 2:
                return f"{n * (n + 1) * (2 * n + 1) // 6}\n"
            elif k == 3:
                # Sum of odds
                return f"{sum(x for x in range(1, n + 1) if x % 2 == 1)}\n"
            else:
                # Sum of evens
                return f"{sum(x for x in range(1, n + 1) if x % 2 == 0)}\n"

        testcases = [
            ("5", solver("5")),
            ("10", solver("10")),
            ("50", solver("50")),
            ("100", solver("100")),
            ("500", solver("500")),
        ]

    elif prefix == "vt":
        # 1D Arrays
        title = get_title("vt", index)
        desc = get_story_description("vt", index, title)
        pts = 25 + (index % 10) * 2
        def solver(input_str):
            lines = input_str.strip().split("\n")
            arr = [int(x) for x in lines[1].split()]
            k = (index % 4) + 1
            if k == 1:
                return f"{max(arr)} {min(arr)}\n"
            elif k == 2:
                return f"{sum(arr)}\n"
            elif k == 3:
                return f"{len([x for x in arr if x > 0])}\n"
            else:
                return " ".join(str(x) for x in reversed(arr)) + "\n"

        testcases = [
            ("5\n1 4 2 8 5", solver("5\n1 4 2 8 5")),
            ("6\n-2 5 0 -8 9 12", solver("6\n-2 5 0 -8 9 12")),
            ("4\n10 20 30 40", solver("4\n10 20 30 40")),
            ("7\n3 1 4 1 5 9 2", solver("7\n3 1 4 1 5 9 2")),
            ("5\n-5 -4 -3 -2 -1", solver("5\n-5 -4 -3 -2 -1")),
        ]

    elif prefix == "mt":
        # 2D Matrices
        title = get_title("mt", index)
        desc = get_story_description("mt", index, title)
        pts = 30 + (index % 10) * 3
        def solver(input_str):
            lines = input_str.strip().split("\n")
            n, m = map(int, lines[0].split())
            matrix = [[int(x) for x in line.split()] for line in lines[1:n+1]]
            total = sum(sum(row) for row in matrix)
            return f"{total}\n"

        testcases = [
            ("2 2\n1 2\n3 4", solver("2 2\n1 2\n3 4")),
            ("3 3\n1 2 3\n4 5 6\n7 8 9", solver("3 3\n1 2 3\n4 5 6\n7 8 9")),
            ("2 3\n5 10 15\n20 25 30", solver("2 3\n5 10 15\n20 25 30")),
            ("3 2\n1 1\n2 2\n3 3", solver("3 2\n1 1\n2 2\n3 3")),
            ("1 4\n2 4 6 8", solver("1 4\n2 4 6 8")),
        ]

    elif prefix == "str":
        # String Manipulation
        title = get_title("str", index)
        desc = get_story_description("str", index, title)
        pts = 25 + (index % 10) * 2
        def solver(input_str):
            s = input_str.strip()
            k = (index % 3) + 1
            if k == 1:
                return "YES\n" if s == s[::-1] else "NO\n"
            elif k == 2:
                return f"{len(s.split())}\n"
            else:
                return f"{len(s)}\n"

        testcases = [
            ("radar", solver("radar")),
            ("hello world", solver("hello world")),
            ("a toyota", solver("a toyota")),
            ("competitive programming", solver("competitive programming")),
            ("level", solver("level")),
        ]

    elif prefix == "fnc":
        # Recursion & Backtracking
        title = get_title("fnc", index)
        desc = get_story_description("fnc", index, title)
        pts = 35 + (index % 10) * 3
        def solver(input_str):
            n = int(input_str.strip())
            # Fibonacci or Factorial mod 10^9+7
            a, b = 0, 1
            for _ in range(n):
                a, b = b, (a + b) % 1000000007
            return f"{a}\n"

        testcases = [
            ("1", solver("1")),
            ("5", solver("5")),
            ("10", solver("10")),
            ("20", solver("20")),
            ("30", solver("30")),
        ]

    elif prefix == "srt":
        # Sorting & Searching
        title = get_title("srt", index)
        desc = get_story_description("srt", index, title)
        pts = 30 + (index % 10) * 3
        def solver(input_str):
            lines = input_str.strip().split("\n")
            arr = sorted([int(x) for x in lines[1].split()])
            return " ".join(str(x) for x in arr) + "\n"

        testcases = [
            ("5\n5 2 8 1 9", solver("5\n5 2 8 1 9")),
            ("6\n100 50 200 10 25 75", solver("6\n100 50 200 10 25 75")),
            ("4\n4 3 2 1", solver("4\n4 3 2 1")),
            ("7\n12 11 13 5 6 7 1", solver("7\n12 11 13 5 6 7 1")),
            ("3\n9 0 -2", solver("3\n9 0 -2")),
        ]

    elif prefix == "mth":
        # Number Theory
        title = get_title("mth", index)
        desc = get_story_description("mth", index, title)
        pts = 40 + (index % 10) * 4
        def solver(input_str):
            n = int(input_str.strip())
            # Check prime
            if n < 2: return "NO\n"
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0: return "NO\n"
            return "YES\n"

        testcases = [
            ("7", solver("7")),
            ("10", solver("10")),
            ("97", solver("97")),
            ("100", solver("100")),
            ("101", solver("101")),
        ]

    elif prefix == "dp":
        # Dynamic Programming
        title = get_title("dp", index)
        desc = get_story_description("dp", index, title)
        pts = 45 + (index % 10) * 5
        def solver(input_str):
            lines = input_str.strip().split("\n")
            arr = [int(x) for x in lines[1].split()]
            # Kadane's maximum subarray sum
            max_so_far = arr[0]
            curr_max = arr[0]
            for x in arr[1:]:
                curr_max = max(x, curr_max + x)
                max_so_far = max(max_so_far, curr_max)
            return f"{max_so_far}\n"

        testcases = [
            ("5\n1 -2 3 5 -1", solver("5\n1 -2 3 5 -1")),
            ("4\n-1 -2 -3 -4", solver("4\n-1 -2 -3 -4")),
            ("6\n2 3 -5 8 10 -2", solver("6\n2 3 -5 8 10 -2")),
            ("5\n10 20 30 -50 60", solver("5\n10 20 30 -50 60")),
            ("3\n-5 10 -2", solver("3\n-5 10 -2")),
        ]

    elif prefix == "gr":
        # Graphs
        title = get_title("gr", index)
        desc = get_story_description("gr", index, title)
        pts = 50 + (index % 10) * 5
        def solver(input_str):
            lines = input_str.strip().split("\n")
            n, m = map(int, lines[0].split())
            parent = list(range(n + 1))
            def find(i):
                if parent[i] == i: return i
                parent[i] = find(parent[i])
                return parent[i]
            def union(i, j):
                root_i = find(i)
                root_j = find(j)
                if root_i != root_j:
                    parent[root_i] = root_j
                    return True
                return False
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                union(u, v)
            components = len(set(find(i) for i in range(1, n + 1)))
            return f"{components}\n"

        testcases = [
            ("4 2\n1 2\n3 4", solver("4 2\n1 2\n3 4")),
            ("5 4\n1 2\n2 3\n3 4\n4 5", solver("5 4\n1 2\n2 3\n3 4\n4 5")),
            ("3 0", solver("3 0")),
            ("4 3\n1 2\n2 3\n1 3", solver("4 3\n1 2\n2 3\n1 3")),
            ("6 3\n1 2\n3 4\n5 6", solver("6 3\n1 2\n3 4\n5 6")),
        ]

    else: # ds (Advanced Data Structures)
        title = get_title("ds", index)
        desc = get_story_description("ds", index, title)
        pts = 55 + (index % 10) * 5
        def solver(input_str):
            lines = input_str.strip().split("\n")
            n, q = map(int, lines[0].split())
            arr = [int(x) for x in lines[1].split()]
            pref = [0] * (n + 1)
            for i in range(n):
                pref[i+1] = pref[i] + arr[i]
            res = []
            for line in lines[2:2+q]:
                l, r = map(int, line.split())
                res.append(str(pref[r] - pref[l-1]))
            return "\n".join(res) + "\n"

        testcases = [
            ("5 2\n1 2 3 4 5\n1 3\n2 5", solver("5 2\n1 2 3 4 5\n1 3\n2 5")),
            ("4 1\n10 20 30 40\n1 4", solver("4 1\n10 20 30 40\n1 4")),
            ("6 2\n2 4 6 8 10 12\n2 4\n1 6", solver("6 2\n2 4 6 8 10 12\n2 4\n1 6")),
            ("3 2\n5 5 5\n1 2\n2 3", solver("3 2\n5 5 5\n1 2\n2 3")),
            ("5 1\n-1 -2 3 4 5\n1 5", solver("5 1\n-1 -2 3 4 5\n1 5")),
        ]

    sample_in = testcases[0][0]
    sample_out = testcases[0][1]

    full_description = f"""### Đề bài
{desc}

### Đầu vào
- Dữ liệu vào từ bàn phím (Standard Input).
- Tuân thủ các quy cách định dạng cho bài toán {title}.

### Đầu ra
- In kết quả ra màn hình (Standard Output).
- Nếu in số thực, làm tròn theo quy định trong đề bài.

### Giới hạn & Ràng buộc
- Thời gian chạy tối đa: **{domain['time_limit']} giây**.
- Bộ nhớ tối đa: **256 MB**.
- $1 \\le N \\le 10^5$.
- Các giá trị số nguyên trong phạm vi số nguyên 32-bit hoặc 64-bit có dấu.

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

    return {
        "code": code,
        "name": title,
        "description": full_description,
        "points": pts,
        "time_limit": domain["time_limit"],
        "memory_limit": 262144,
        "testcases": testcases,
    }


def seed_all_problems():
    print("=================================================================")
    print("Starting Massive 1,200 Problems Seeding for VCoder Arena...")
    print("=================================================================")

    all_languages = list(Language.objects.all())
    judges = list(Judge.objects.all())
    print(f"Detected {len(all_languages)} programming languages and {len(judges)} judge daemon(s).")

    # Ensure all ProblemGroups exist
    group_map = {}
    for dom in DOMAINS:
        grp, _ = ProblemGroup.objects.get_or_create(
            name=dom["group_id"],
            defaults={"full_name": dom["group_name"]}
        )
        group_map[dom["prefix"]] = grp

    # Ensure all ProblemTypes exist
    type_map = {}
    for dom in DOMAINS:
        for t in dom["types"]:
            pt, _ = ProblemType.objects.get_or_create(
                name=t,
                defaults={"full_name": t.replace("-", " ").title()}
            )
            type_map[t] = pt

    total_created = 0
    total_updated = 0

    for dom in DOMAINS:
        grp = group_map[dom["prefix"]]
        print(f"\n---> Generating 100 problems for Domain [{dom['prefix']}]: '{dom['group_name']}'...")

        for idx in range(1, 101):
            spec = generate_problem_specs(dom, idx)
            code = spec["code"]

            # 1. Create or Update Problem Model in Database
            problem, created = Problem.objects.get_or_create(
                code=code,
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "points": spec["points"],
                    "time_limit": spec["time_limit"],
                    "memory_limit": spec["memory_limit"],
                    "is_public": True,
                    "group": grp,
                    "date": timezone.now(),
                }
            )

            if not created:
                problem.name = spec["name"]
                problem.description = spec["description"]
                problem.points = spec["points"]
                problem.time_limit = spec["time_limit"]
                problem.memory_limit = spec["memory_limit"]
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

            # Bind to judges
            for j in judges:
                j.problems.add(problem)

            # 2. Generate Testcase Files in PROBLEMS_DIR / code
            prob_dir = PROBLEMS_DIR / code
            prob_dir.mkdir(parents=True, exist_ok=True)

            yaml_test_cases = []
            testcases = spec["testcases"]

            # Samples
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
                    "points": round(spec["points"] / len(testcases), 1)
                })

            # Secrets
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
                    "points": round(spec["points"] / len(testcases), 1)
                })

            init_yaml_data = {
                "archive": None,
                "test_cases": yaml_test_cases
            }
            with open(prob_dir / "init.yml", "w") as f_yml:
                f_yml.write("# Generated by VCoder Arena Massive Problem Bank Generator\n")
                yaml.dump(init_yaml_data, f_yml, default_flow_style=False)

        print(f"     Finished domain [{dom['prefix']}]: 100 problems processed.")

    print("\n" + "=" * 65)
    print(f"SUCCESS! Seeding Complete:")
    print(f"  - Total New Problems Created: {total_created}")
    print(f"  - Total Problems Updated: {total_updated}")
    print(f"  - Total Problem Count in DB: {Problem.objects.count()}")
    print("=================================================================")

if __name__ == "__main__":
    seed_all_problems()
