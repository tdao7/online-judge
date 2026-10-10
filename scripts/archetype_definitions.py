# -*- coding: utf-8 -*-
"""
Diverse Competitive Programming Archetypes for 12 Algorithmic Domains.
Each domain has 8-10 distinct problem templates so consecutive problems
in the same domain and adjacent problems in the catalog have completely
different input, output, constraints, and algorithmic solutions.
"""

def get_domain_archetypes(prefix):
    if prefix == "cb":
        return [
            {
                "topic": "Tính tổng hai số nguyên",
                "input_desc": "Một dòng duy nhất chứa hai số nguyên $a$ và $b$ cách nhau bởi dấu cách.",
                "output_desc": "In ra một số nguyên duy nhất là tổng $a + b$.",
                "constraints": "$-10^9 \\le a, b \\le 10^9$.",
                "pts": 10,
                "solver": lambda s: f"{int(s.split()[0]) + int(s.split()[1])}\n",
                "tests": [("5 7", "12\n"), ("12 25", "37\n"), ("100 45", "145\n"), ("250 80", "330\n"), ("1000 333", "1333\n")]
            },
            {
                "topic": "Tính hiệu hai số nguyên",
                "input_desc": "Một dòng duy nhất chứa hai số nguyên $a$ và $b$ cách nhau bởi dấu cách.",
                "output_desc": "In ra một số nguyên duy nhất là hiệu $a - b$.",
                "constraints": "$-10^9 \\le a, b \\le 10^9$.",
                "pts": 10,
                "solver": lambda s: f"{int(s.split()[0]) - int(s.split()[1])}\n",
                "tests": [("10 3", "7\n"), ("25 12", "13\n"), ("50 80", "-30\n"), ("100 100", "0\n"), ("0 15", "-15\n")]
            },
            {
                "topic": "Tính tích hai số nguyên",
                "input_desc": "Một dòng duy nhất chứa hai số nguyên $a$ và $b$ cách nhau bởi dấu cách.",
                "output_desc": "In ra một số nguyên duy nhất là tích $a \\times b$.",
                "constraints": "$-10^4 \\le a, b \\le 10^4$.",
                "pts": 10,
                "solver": lambda s: f"{int(s.split()[0]) * int(s.split()[1])}\n",
                "tests": [("4 6", "24\n"), ("15 8", "120\n"), ("12 12", "144\n"), ("100 20", "2000\n"), ("7 9", "63\n")]
            },
            {
                "topic": "Chia lấy phần nguyên và phần dư",
                "input_desc": "Một dòng duy nhất chứa hai số nguyên dương $a$ và $b$ ($b \\ne 0$).",
                "output_desc": "In ra hai số nguyên cách nhau một khoảng trắng: thương nguyên $a / b$ và số dư $a \\% b$.",
                "constraints": "$1 \\le a, b \\le 10^9$.",
                "pts": 12,
                "solver": lambda s: f"{int(s.split()[0]) // int(s.split()[1])} {int(s.split()[0]) % int(s.split()[1])}\n",
                "tests": [("17 5", "3 2\n"), ("100 3", "33 1\n"), ("45 9", "5 0\n"), ("8 12", "0 8\n"), ("99 10", "9 9\n")]
            },
            {
                "topic": "Chu vi và diện tích hình vuông",
                "input_desc": "Một dòng chứa số nguyên dương $a$ là độ dài cạnh hình vuông.",
                "output_desc": "In ra chu vi và diện tích hình vuông cách nhau bởi dấu cách.",
                "constraints": "$1 \\le a \\le 10^6$.",
                "pts": 12,
                "solver": lambda s: f"{4 * int(s.strip())} {int(s.strip()) ** 2}\n",
                "tests": [("5", "20 25\n"), ("8", "32 64\n"), ("12", "48 144\n"), ("20", "80 400\n"), ("100", "400 10000\n")]
            },
            {
                "topic": "Chu vi và diện tích hình chữ nhật",
                "input_desc": "Một dòng chứa hai số nguyên dương $a$ và $b$ là chiều dài và chiều rộng.",
                "output_desc": "In ra chu vi và diện tích hình chữ nhật cách nhau bởi dấu cách.",
                "constraints": "$1 \\le a, b \\le 10^6$.",
                "pts": 15,
                "solver": lambda s: f"{2 * (int(s.split()[0]) + int(s.split()[1]))} {int(s.split()[0]) * int(s.split()[1])}\n",
                "tests": [("4 7", "22 28\n"), ("10 5", "30 50\n"), ("12 8", "40 96\n"), ("25 4", "58 100\n"), ("50 20", "140 1000\n")]
            },
            {
                "topic": "Diện tích hình tam giác",
                "input_desc": "Một dòng chứa hai số nguyên dương $a$ và $h$ lần lượt là cạnh đáy và chiều cao.",
                "output_desc": "In ra diện tích tam giác làm tròn chính xác 2 chữ số thập phân.",
                "constraints": "$1 \\le a, h \\le 10^5$.",
                "pts": 15,
                "solver": lambda s: f"{0.5 * int(s.split()[0]) * int(s.split()[1]):.2f}\n",
                "tests": [("6 4", "12.00\n"), ("7 5", "17.50\n"), ("10 8", "40.00\n"), ("15 3", "22.50\n"), ("20 11", "110.00\n")]
            },
            {
                "topic": "Chu vi và diện tích hình tròn",
                "input_desc": "Một dòng chứa số thực $r$ là bán kính hình tròn.",
                "output_desc": "In ra chu vi và diện tích hình tròn với $\\pi = 3.14159$, làm tròn 2 chữ số thập phân.",
                "constraints": "$0 < r \\le 10^4$.",
                "pts": 15,
                "solver": lambda s: f"{2 * 3.14159 * float(s.strip()):.2f} {3.14159 * (float(s.strip())**2):.2f}\n",
                "tests": [("3.5", "21.99 38.48\n"), ("5.0", "31.42 78.54\n"), ("10.0", "62.83 314.16\n"), ("2.2", "13.82 15.21\n"), ("7.5", "47.12 176.71\n")]
            },
            {
                "topic": "Quy đổi nhiệt độ Celsius sang Fahrenheit",
                "input_desc": "Một dòng chứa số thực $C$ biểu thị nhiệt độ Celsius.",
                "output_desc": "In ra nhiệt độ Fahrenheit tương ứng theo công thức $F = C \\times 1.8 + 32$, làm tròn 2 chữ số thập phân.",
                "constraints": "$-100 \\le C \\le 1000$.",
                "pts": 15,
                "solver": lambda s: f"{float(s.strip()) * 1.8 + 32.0:.2f}\n",
                "tests": [("0", "32.00\n"), ("100", "212.00\n"), ("37", "98.60\n"), ("-40", "-40.00\n"), ("25", "77.00\n")]
            },
            {
                "topic": "Quy đổi thời gian giây sang Giờ:Phút:Giây",
                "input_desc": "Một dòng duy nhất chứa số nguyên không âm $S$ biểu thị tổng số giây.",
                "output_desc": "In ra định dạng `HH:MM:SS` (với 2 chữ số cho mỗi đơn vị).",
                "constraints": "$0 \\le S \\le 864000$.",
                "pts": 20,
                "solver": lambda s: f"{int(s)//3600:02d}:{(int(s)%3600)//60:02d}:{int(s)%60:02d}\n",
                "tests": [("3665", "01:01:05\n"), ("60", "00:01:00\n"), ("7200", "02:00:00\n"), ("0", "00:00:00\n"), ("86399", "23:59:59\n")]
            }
        ]

    elif prefix == "dp":
        def kadane_solve(s):
            arr = [int(x) for x in s.strip().split("\n")[1].split()]
            c = m = arr[0]
            for x in arr[1:]:
                c = max(x, c + x)
                m = max(m, c)
            return f"{m}\n"

        def stairs_solve(s):
            n = int(s.strip())
            a, b = 1, 1
            for _ in range(n): a, b = b, (a + b) % 1000000007
            return f"{a}\n"

        def robber_solve(s):
            arr = [int(x) for x in s.strip().split("\n")[1].split()]
            if len(arr) == 1: return f"{arr[0]}\n"
            d0, d1 = 0, arr[0]
            for x in arr[1:]: d0, d1 = max(d0, d1), d0 + x
            return f"{max(d0, d1)}\n"

        def lis_solve(s):
            import bisect
            arr = [int(x) for x in s.strip().split("\n")[1].split()]
            tails = []
            for x in arr:
                idx = bisect.bisect_left(tails, x)
                if idx == len(tails): tails.append(x)
                else: tails[idx] = x
            return f"{len(tails)}\n"

        def knapsack_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, w = map(int, lines[0].split())
            weights = [int(x) for x in lines[1].split()]
            values = [int(x) for x in lines[2].split()]
            dp = [0] * (w + 1)
            for wi, vi in zip(weights, values):
                for j in range(w, wi - 1, -1):
                    dp[j] = max(dp[j], dp[j - wi] + vi)
            return f"{dp[w]}\n"

        def coin_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            amt = int(lines[0])
            coins = [int(x) for x in lines[1].split()]
            dp = [float('inf')] * (amt + 1)
            dp[0] = 0
            for c in coins:
                for j in range(c, amt + 1):
                    dp[j] = min(dp[j], dp[j - c] + 1)
            return f"{dp[amt] if dp[amt] != float('inf') else -1}\n"

        def grid_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            grid = [[int(x) for x in l.split()] for l in lines[1:n+1]]
            dp = [[0]*m for _ in range(n)]
            dp[0][0] = grid[0][0]
            for j in range(1, m): dp[0][j] = dp[0][j-1] + grid[0][j]
            for i in range(1, n): dp[i][0] = dp[i-1][0] + grid[i][0]
            for i in range(1, n):
                for j in range(1, m):
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]
            return f"{dp[n-1][m-1]}\n"

        def rod_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n = int(lines[0])
            prices = [int(x) for x in lines[1].split()]
            dp = [0] * (n + 1)
            for i in range(1, n + 1):
                mx = 0
                for j in range(1, i + 1):
                    if j - 1 < len(prices):
                        mx = max(mx, prices[j-1] + dp[i-j])
                dp[i] = mx
            return f"{dp[n]}\n"

        return [
            {
                "topic": "Đoạn con có tổng lớn nhất (Kadane)",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên $A_1, A_2, \\dots, A_N$.",
                "output_desc": "In ra tổng lớn nhất của một dãy con liên tiếp.",
                "constraints": "$1 \\le N \\le 10^5, -10^4 \\le A_i \\le 10^4$.",
                "pts": 45,
                "solver": kadane_solve,
                "tests": [("5\n1 -2 3 5 -1", "8\n"), ("4\n-1 -2 -3 -4", "-1\n"), ("6\n2 3 -5 8 10 -2", "18\n"), ("5\n10 20 30 -50 60", "70\n"), ("3\n-5 10 -2", "10\n")]
            },
            {
                "topic": "Số cách bước lên bậc thang (Fibonacci DP)",
                "input_desc": "Một dòng duy nhất chứa số nguyên dương $N$ là số bậc thang.",
                "output_desc": "In ra số cách bước lên bậc thứ $N$ modulo $10^9+7$ (mỗi bước có thể đi 1 hoặc 2 bậc).",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 45,
                "solver": stairs_solve,
                "tests": [("1", "1\n"), ("2", "2\n"), ("3", "3\n"), ("5", "8\n"), ("10", "89\n")]
            },
            {
                "topic": "Tổng lớn nhất của các phần tử không kề nhau (House Robber)",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên không âm $A_1, A_2, \\dots, A_N$.",
                "output_desc": "In ra tổng lớn nhất có thể thu được sao cho không chọn hai phần tử liên tiếp.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le A_i \\le 10^4$.",
                "pts": 50,
                "solver": robber_solve,
                "tests": [("4\n1 2 3 1", "4\n"), ("5\n2 7 9 3 1", "12\n"), ("3\n5 1 5", "10\n"), ("4\n10 20 15 30", "50\n"), ("5\n4 1 2 7 5", "11\n")]
            },
            {
                "topic": "Độ dài dãy con tăng dài nhất (LIS)",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên $A_1, A_2, \\dots, A_N$.",
                "output_desc": "In ra độ dài của dãy con tăng dài nhất (các phần tử strictly increasing).",
                "constraints": "$1 \\le N \\le 10^5, -10^9 \\le A_i \\le 10^9$.",
                "pts": 55,
                "solver": lis_solve,
                "tests": [("6\n10 9 2 5 3 7", "3\n"), ("6\n0 1 0 3 2 3", "4\n"), ("7\n7 7 7 7 7 7 7", "1\n"), ("5\n5 4 3 2 1", "1\n"), ("5\n1 3 2 4 5", "4\n")]
            },
            {
                "topic": "Bài toán cái túi Knapsack 0/1",
                "input_desc": "Dòng 1: Hai số nguyên $N$ (số đồ vật) và $W$ (sức chứa balo). Dòng 2: $N$ trọng lượng $w_i$. Dòng 3: $N$ giá trị $v_i$.",
                "output_desc": "In ra tổng giá trị lớn nhất có thể xếp vào balo mà không vượt quá tải trọng $W$.",
                "constraints": "$1 \\le N \\le 1000, 1 \\le W \\le 5000, 1 \\le w_i, v_i \\le 1000$.",
                "pts": 60,
                "solver": knapsack_solve,
                "tests": [
                    ("3 50\n10 20 30\n60 100 120", "220\n"),
                    ("4 5\n2 1 3 2\n12 10 20 15", "37\n"),
                    ("3 4\n1 2 3\n10 15 40", "50\n"),
                    ("2 10\n5 6\n10 12", "12\n"),
                    ("4 8\n2 3 4 5\n3 4 5 8", "12\n")
                ]
            },
            {
                "topic": "Đổi tiền xu với số đồng xu ít nhất (Coin Change)",
                "input_desc": "Dòng 1: Số tiền cần đổi $S$. Dòng 2: Danh sách các mệnh giá tiền xu.",
                "output_desc": "In ra số đồng xu tối thiểu để đổi được số tiền $S$. Nếu không thể đổi, in ra -1.",
                "constraints": "$1 \\le S \\le 10^4$, số loại tiền $\\le 50$.",
                "pts": 60,
                "solver": coin_solve,
                "tests": [
                    ("11\n1 2 5", "3\n"),
                    ("3\n2", "-1\n"),
                    ("0\n1", "0\n"),
                    ("15\n2 5 10", "2\n"),
                    ("7\n3 5", "-1\n")
                ]
            },
            {
                "topic": "Đường đi có tổng chi phí nhỏ nhất trên lưới (Grid Min Path)",
                "input_desc": "Dòng 1: Hai số nguyên $N, M$. $N$ dòng tiếp theo, mỗi dòng chứa $M$ số nguyên biểu thị chi phí các ô.",
                "output_desc": "In ra chi phí nhỏ nhất để di chuyển từ ô $(1, 1)$ đến $(N, M)$ (chỉ đi sang phải hoặc xuống dưới).",
                "constraints": "$1 \\le N, M \\le 500, 0 \\le A_{i,j} \\le 1000$.",
                "pts": 65,
                "solver": grid_solve,
                "tests": [
                    ("3 3\n1 3 1\n1 5 1\n4 2 1", "7\n"),
                    ("2 3\n1 2 3\n4 5 6", "12\n"),
                    ("2 2\n5 10\n15 20", "35\n"),
                    ("3 2\n1 1\n2 2\n3 3", "7\n"),
                    ("1 4\n2 4 6 8", "20\n")
                ]
            },
            {
                "topic": "Bài toán cắt thanh kim loại tối ưu (Rod Cutting)",
                "input_desc": "Dòng 1: Độ dài thanh kim loại $N$. Dòng 2: Bảng giá cho các đoạn dài từ $1$ đến $N$.",
                "output_desc": "In ra lợi nhuận lớn nhất có thể thu được khi cắt thanh kim loại.",
                "constraints": "$1 \\le N \\le 1000$.",
                "pts": 70,
                "solver": rod_solve,
                "tests": [
                    ("4\n1 5 8 9", "10\n"),
                    ("5\n2 5 7 8 10", "12\n"),
                    ("3\n1 5 8", "8\n"),
                    ("2\n3 5", "6\n"),
                    ("6\n1 5 8 9 10 17", "17\n")
                ]
            }
        ]

    elif prefix == "str":
        return [
            {
                "topic": "Kiểm tra chuỗi đối xứng (Palindrome)",
                "input_desc": "Một dòng duy nhất chứa chuỗi ký tự $S$ (không chứa khoảng trắng).",
                "output_desc": "In ra `YES` nếu $S$ là chuỗi đối xứng, ngược lại in ra `NO`.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: "YES\n" if s.strip() == s.strip()[::-1] else "NO\n",
                "tests": [("radar", "YES\n"), ("hello", "NO\n"), ("level", "YES\n"), ("noon", "YES\n"), ("abcba", "YES\n")]
            },
            {
                "topic": "Đếm số lượng từ trong đoạn văn",
                "input_desc": "Một dòng chứa đoạn văn bản gồm các từ cách nhau bởi một hoặc nhiều khoảng trắng.",
                "output_desc": "In ra một số nguyên duy nhất là số lượng từ trong đoạn văn.",
                "constraints": "Chiều dài đoạn văn không quá $10^5$ ký tự.",
                "pts": 25,
                "solver": lambda s: f"{len(s.strip().split())}\n",
                "tests": [("hello world", "2\n"), ("  competitive   programming  ", "2\n"), ("a b c d e", "5\n"), ("luyencode net", "2\n"), ("one", "1\n")]
            },
            {
                "topic": "Đếm số ký tự nguyên âm",
                "input_desc": "Một dòng duy nhất chứa chuỗi văn bản $S$.",
                "output_desc": "In ra số lượng chữ cái nguyên âm tiếng Anh (a, e, i, o, u) không phân biệt hoa thường.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{len([c for c in s.strip().lower() if c in 'aeiou'])}\n",
                "tests": [("Programming", "3\n"), ("Education", "5\n"), ("Rhythm", "0\n"), ("VCoder", "2\n"), ("Antigravity", "4\n")]
            },
            {
                "topic": "Đảo ngược chuỗi ký tự",
                "input_desc": "Một dòng chứa chuỗi ký tự $S$.",
                "output_desc": "In ra chuỗi $S$ theo thứ tự đảo ngược.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{s.strip()[::-1]}\n",
                "tests": [("abcdef", "fedcba\n"), ("12345", "54321\n"), ("radar", "radar\n"), ("Hello", "olleH\n"), ("DMOJ", "JOMD\n")]
            },
            {
                "topic": "Chuyển chuỗi sang CHỮ HOA",
                "input_desc": "Một dòng chứa chuỗi ký tự $S$.",
                "output_desc": "In ra chuỗi $S$ sau khi đã chuyển tất cả các chữ cái thành chữ in hoa.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{s.strip().upper()}\n",
                "tests": [("hello", "HELLO\n"), ("competitive programming", "COMPETITIVE PROGRAMMING\n"), ("VcOdEr", "VCODER\n"), ("abc 123", "ABC 123\n"), ("lowercase", "LOWERCASE\n")]
            },
            {
                "topic": "Đếm số chữ số trong chuỗi",
                "input_desc": "Một dòng chứa chuỗi ký tự $S$.",
                "output_desc": "In ra số lượng ký tự là chữ số (0-9) xuất hiện trong chuỗi.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{len([c for c in s.strip() if c.isdigit()])}\n",
                "tests": [("user1234", "4\n"), ("no_digits", "0\n"), ("year2026month10day10", "8\n"), ("9876543210", "10\n"), ("Room 404 Not Found 500", "6\n")]
            },
            {
                "topic": "Xóa toàn bộ khoảng trắng trong chuỗi",
                "input_desc": "Một dòng chứa chuỗi ký tự $S$.",
                "output_desc": "In ra chuỗi sau khi loại bỏ tất cả các khoảng trắng.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{s.strip().replace(' ', '')}\n",
                "tests": [("a b c d", "abcd\n"), ("  hello   world  ", "helloworld\n"), ("VCoder Arena", "VCoderArena\n"), ("1 2 3 4 5", "12345\n"), ("no_space", "no_space\n")]
            },
            {
                "topic": "Kiểm tra chuỗi chỉ chứa chữ số",
                "input_desc": "Một dòng chứa chuỗi ký tự $S$.",
                "output_desc": "In ra `YES` nếu chuỗi chỉ gồm các ký tự chữ số, ngược lại in ra `NO`.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: "YES\n" if s.strip().isdigit() else "NO\n",
                "tests": [("123456", "YES\n"), ("123a45", "NO\n"), ("00982", "YES\n"), ("hello", "NO\n"), ("1", "YES\n")]
            }
        ]

    elif prefix == "gr":
        def cc_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            parent = list(range(n + 1))
            def find(i):
                if parent[i] == i: return i
                parent[i] = find(parent[i])
                return parent[i]
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                ru, rv = find(u), find(v)
                if ru != rv: parent[ru] = rv
            comps = len(set(find(i) for i in range(1, n + 1)))
            return f"{comps}\n"

        def is_conn_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            if n == 1: return "YES\n"
            parent = list(range(n + 1))
            def find(i):
                if parent[i] == i: return i
                parent[i] = find(parent[i])
                return parent[i]
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                ru, rv = find(u), find(v)
                if ru != rv: parent[ru] = rv
            comps = len(set(find(i) for i in range(1, n + 1)))
            return "YES\n" if comps == 1 else "NO\n"

        def bfs_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            adj = {i: [] for i in range(1, n + 1)}
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                adj[u].append(v)
                adj[v].append(u)
            from collections import deque
            q = deque([(1, 0)])
            visited = {1}
            dist = -1
            while q:
                u, d = q.popleft()
                if u == n:
                    dist = d
                    break
                for v in adj[u]:
                    if v not in visited:
                        visited.add(v)
                        q.append((v, d + 1))
            return f"{dist}\n"

        def max_deg_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            deg = [0] * (n + 1)
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                deg[u] += 1
                deg[v] += 1
            return f"{max(deg[1:]) if n > 0 else 0}\n"

        def iso_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            deg = [0] * (n + 1)
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                deg[u] += 1
                deg[v] += 1
            return f"{deg[1:].count(0)}\n"

        def edge_count_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            return f"{m}\n"

        def cycle_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            parent = list(range(n + 1))
            def find(i):
                if parent[i] == i: return i
                parent[i] = find(parent[i])
                return parent[i]
            has_c = False
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                ru, rv = find(u), find(v)
                if ru == rv: has_c = True
                else: parent[ru] = rv
            return "YES\n" if has_c else "NO\n"

        def leaf_count_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, m = map(int, lines[0].split())
            deg = [0] * (n + 1)
            for line in lines[1:m+1]:
                u, v = map(int, line.split())
                deg[u] += 1
                deg[v] += 1
            return f"{deg[1:].count(1)}\n"

        return [
            {
                "topic": "Đếm số thành phần liên thông",
                "input_desc": "Dòng 1: Hai số nguyên $N$ (đỉnh) và $M$ (cạnh). $M$ dòng tiếp theo, mỗi dòng chứa hai đỉnh $u, v$.",
                "output_desc": "In ra số lượng thành phần liên thông của đồ thị.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 50,
                "solver": cc_solve,
                "tests": [("4 2\n1 2\n3 4", "2\n"), ("5 4\n1 2\n2 3\n3 4\n4 5", "1\n"), ("3 0", "3\n"), ("4 3\n1 2\n2 3\n1 3", "2\n"), ("6 3\n1 2\n3 4\n5 6", "3\n")]
            },
            {
                "topic": "Kiểm tra tính liên thông của đồ thị",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo, mỗi dòng chứa một cạnh $u, v$.",
                "output_desc": "In ra `YES` nếu đồ thị liên thông, ngược lại in ra `NO`.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 50,
                "solver": is_conn_solve,
                "tests": [("3 2\n1 2\n2 3", "YES\n"), ("4 2\n1 2\n3 4", "NO\n"), ("1 0", "YES\n"), ("5 4\n1 2\n2 3\n3 4\n4 5", "YES\n"), ("3 1\n1 2", "NO\n")]
            },
            {
                "topic": "Đường đi ngắn nhất giữa hai đỉnh (BFS)",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo biểu thị các cạnh vô hướng.",
                "output_desc": "In ra số cạnh trên đường đi ngắn nhất từ đỉnh 1 đến đỉnh $N$. Nếu không thể đến, in ra -1.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 55,
                "solver": bfs_solve,
                "tests": [("4 4\n1 2\n2 3\n3 4\n1 4", "1\n"), ("3 1\n1 2", "-1\n"), ("5 4\n1 2\n2 3\n3 4\n4 5", "4\n"), ("3 2\n1 2\n2 3", "2\n"), ("2 0", "-1\n")]
            },
            {
                "topic": "Tìm bậc lớn nhất của đỉnh trong đồ thị",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo chứa các cạnh vô hướng.",
                "output_desc": "In ra bậc lớn nhất của một đỉnh bất kỳ trong đồ thị.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 50,
                "solver": max_deg_solve,
                "tests": [("4 3\n1 2\n1 3\n1 4", "3\n"), ("3 3\n1 2\n2 3\n3 1", "2\n"), ("5 0", "0\n"), ("4 2\n1 2\n3 4", "1\n"), ("5 4\n1 2\n1 3\n1 4\n1 5", "4\n")]
            },
            {
                "topic": "Đếm số đỉnh cô lập trong mạng lưới",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo chứa các cạnh.",
                "output_desc": "In ra số lượng đỉnh cô lập (có bậc bằng 0).",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 50,
                "solver": iso_solve,
                "tests": [("4 1\n1 2", "2\n"), ("3 3\n1 2\n2 3\n3 1", "0\n"), ("5 0", "5\n"), ("5 2\n1 2\n3 4", "1\n"), ("6 2\n1 2\n3 4", "2\n")]
            },
            {
                "topic": "Kiểm tra chu trình trong đồ thị vô hướng",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo chứa các cạnh.",
                "output_desc": "In ra `YES` nếu đồ thị chứa ít nhất một chu trình, ngược lại in ra `NO`.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 55,
                "solver": cycle_solve,
                "tests": [("3 3\n1 2\n2 3\n3 1", "YES\n"), ("3 2\n1 2\n2 3", "NO\n"), ("4 3\n1 2\n2 3\n3 4", "NO\n"), ("4 4\n1 2\n2 3\n3 4\n4 1", "YES\n"), ("2 1\n1 2", "NO\n")]
            },
            {
                "topic": "Đếm số cạnh của đồ thị",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$. $M$ dòng tiếp theo chứa danh sách cạnh.",
                "output_desc": "In ra tổng số cạnh $M$.",
                "constraints": "$1 \\le N \\le 10^5, 0 \\le M \\le 2 \\times 10^5$.",
                "pts": 45,
                "solver": edge_count_solve,
                "tests": [("4 3\n1 2\n2 3\n3 4", "3\n"), ("5 0", "0\n"), ("3 3\n1 2\n2 3\n3 1", "3\n"), ("10 5\n1 2\n2 3\n3 4\n4 5\n5 6", "5\n"), ("2 1\n1 2", "1\n")]
            },
            {
                "topic": "Đếm số nút lá trong cây",
                "input_desc": "Dòng 1: Hai số nguyên $N$ và $M$ ($M = N - 1$). $M$ dòng tiếp theo chứa các cạnh của cây.",
                "output_desc": "In ra số lượng nút lá (nút có bậc bằng 1).",
                "constraints": "$2 \\le N \\le 10^5, M = N - 1$.",
                "pts": 55,
                "solver": leaf_count_solve,
                "tests": [("4 3\n1 2\n1 3\n1 4", "3\n"), ("3 2\n1 2\n2 3", "2\n"), ("5 4\n1 2\n2 3\n3 4\n4 5", "2\n"), ("5 4\n1 2\n1 3\n2 4\n2 5", "3\n"), ("2 1\n1 2", "2\n")]
            }
        ]

    elif prefix == "dk":
        def even_odd(s): return "EVEN\n" if int(s.strip()) % 2 == 0 else "ODD\n"
        def max2(s): nums = [int(x) for x in s.split()]; return f"{max(nums[0], nums[1])}\n"
        def max3(s): nums = [int(x) for x in s.split()]; return f"{max(nums)}\n"
        def min3(s): nums = [int(x) for x in s.split()]; return f"{min(nums)}\n"
        def leap_year(s):
            y = int(s.strip())
            return "YES\n" if (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0) else "NO\n"
        def tri_type(s):
            a, b, c = sorted([float(x) for x in s.split()][:3])
            if a + b <= c: return "INVALID\n"
            if a == b == c: return "EQUILATERAL\n"
            if a == b or b == c: return "ISOSCELES\n"
            return "SCALENE\n"
        def linear_eq(s):
            a, b = [float(x) for x in s.split()]
            if a == 0: return "NO SOLUTION\n" if b != 0 else "INFINITE\n"
            return f"{-b / a:.2f}\n"
        def bmi(s):
            w, h = [float(x) for x in s.split()]
            val = w / (h * h)
            if val < 18.5: return "UNDERWEIGHT\n"
            if val < 25.0: return "NORMAL\n"
            if val < 30.0: return "OVERWEIGHT\n"
            return "OBESE\n"

        return [
            {
                "topic": "Kiểm tra tính chẵn lẻ",
                "input_desc": "Một dòng chứa số nguyên $N$.",
                "output_desc": "In `EVEN` nếu $N$ chẵn, ngược lại in `ODD`.",
                "constraints": "$-10^9 \\le N \\le 10^9$.",
                "pts": 15,
                "solver": even_odd,
                "tests": [("4", "EVEN\n"), ("7", "ODD\n"), ("12", "EVEN\n"), ("101", "ODD\n"), ("0", "EVEN\n")]
            },
            {
                "topic": "Tìm số lớn nhất trong hai số",
                "input_desc": "Một dòng chứa hai số nguyên $a, b$.",
                "output_desc": "In ra giá trị lớn nhất.",
                "constraints": "$-10^9 \\le a, b \\le 10^9$.",
                "pts": 15,
                "solver": max2,
                "tests": [("4 7", "7\n"), ("10 2", "10\n"), ("-5 3", "3\n"), ("100 100", "100\n"), ("0 -1", "0\n")]
            },
            {
                "topic": "Tìm số lớn nhất trong ba số",
                "input_desc": "Một dòng chứa ba số nguyên $a, b, c$.",
                "output_desc": "In ra giá trị lớn nhất.",
                "constraints": "$-10^9 \\le a, b, c \\le 10^9$.",
                "pts": 15,
                "solver": max3,
                "tests": [("1 5 3", "5\n"), ("9 2 4", "9\n"), ("-1 -5 -2", "-1\n"), ("10 10 5", "10\n"), ("0 0 0", "0\n")]
            },
            {
                "topic": "Tìm số nhỏ nhất trong ba số",
                "input_desc": "Một dòng chứa ba số nguyên $a, b, c$.",
                "output_desc": "In ra giá trị nhỏ nhất.",
                "constraints": "$-10^9 \\le a, b, c \\le 10^9$.",
                "pts": 15,
                "solver": min3,
                "tests": [("1 5 3", "1\n"), ("9 2 4", "2\n"), ("-1 -5 -2", "-5\n"), ("10 10 5", "5\n"), ("0 0 0", "0\n")]
            },
            {
                "topic": "Kiểm tra năm nhuận",
                "input_desc": "Một dòng chứa số nguyên dương $Y$ biểu thị năm.",
                "output_desc": "In `YES` nếu là năm nhuận, ngược lại in `NO`.",
                "constraints": "$1 \\le Y \\le 10^5$.",
                "pts": 20,
                "solver": leap_year,
                "tests": [("2024", "YES\n"), ("1900", "NO\n"), ("2000", "YES\n"), ("2023", "NO\n"), ("2004", "YES\n")]
            },
            {
                "topic": "Phân loại tam giác theo độ dài cạnh",
                "input_desc": "Một dòng chứa ba số thực dương $a, b, c$.",
                "output_desc": "In `EQUILATERAL`, `ISOSCELES`, `SCALENE` hoặc `INVALID`.",
                "constraints": "$0 < a, b, c \\le 10^4$.",
                "pts": 20,
                "solver": tri_type,
                "tests": [("3 4 5", "SCALENE\n"), ("5 5 5", "EQUILATERAL\n"), ("4 4 6", "ISOSCELES\n"), ("1 2 3", "INVALID\n"), ("6 8 10", "SCALENE\n")]
            },
            {
                "topic": "Giải phương trình bậc nhất ax + b = 0",
                "input_desc": "Một dòng chứa hai số thực $a, b$.",
                "output_desc": "In nghiệm với 2 chữ số thập phân, hoặc `NO SOLUTION`, `INFINITE`.",
                "constraints": "$-10^4 \\le a, b \\le 10^4$.",
                "pts": 20,
                "solver": linear_eq,
                "tests": [("2 -4", "2.00\n"), ("5 10", "-2.00\n"), ("3 0", "-0.00\n"), ("4 7", "-1.75\n"), ("-2 8", "4.00\n")]
            },
            {
                "topic": "Đánh giá chỉ số thể chất BMI",
                "input_desc": "Một dòng chứa cân nặng $w$ (kg) và chiều cao $h$ (m).",
                "output_desc": "In `UNDERWEIGHT`, `NORMAL`, `OVERWEIGHT`, hoặc `OBESE`.",
                "constraints": "$10 \\le w \\le 250, 0.5 \\le h \\le 2.5$.",
                "pts": 25,
                "solver": bmi,
                "tests": [("60 1.7", "NORMAL\n"), ("75 1.75", "NORMAL\n"), ("50 1.6", "NORMAL\n"), ("90 1.8", "OVERWEIGHT\n"), ("45 1.55", "NORMAL\n")]
            }
        ]

    elif prefix == "mth":
        def is_prime(s):
            n = int(s.strip())
            if n < 2: return "NO\n"
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0: return "NO\n"
            return "YES\n"

        def count_divs(s):
            n = int(s.strip())
            c = 0
            for i in range(1, int(n**0.5) + 1):
                if n % i == 0:
                    c += 1 if i * i == n else 2
            return f"{c}\n"

        def gcd_lcm(s):
            a, b = map(int, s.split())
            import math
            g = math.gcd(a, b)
            l = (a * b) // g
            return f"{g} {l}\n"

        def is_sq(s):
            n = int(s.strip())
            if n < 0: return "NO\n"
            r = int(n**0.5)
            return "YES\n" if r * r == n else "NO\n"

        def trailing_zeros(s):
            n = int(s.strip())
            count = 0
            while n >= 5:
                count += n // 5
                n //= 5
            return f"{count}\n"

        def sum_digits(s):
            n = int(s.strip())
            return f"{sum(int(c) for c in str(abs(n)))}\n"

        def mod_exp(s):
            a, b, m = map(int, s.split())
            return f"{pow(a, b, m)}\n"

        def phi(s):
            n = int(s.strip())
            res = n
            p = 2
            while p * p <= n:
                if n % p == 0:
                    while n % p == 0: n //= p
                    res -= res // p
                p += 1
            if n > 1: res -= res // n
            return f"{res}\n"

        return [
            {
                "topic": "Kiểm tra số nguyên tố",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In `YES` nếu $N$ là số nguyên tố, ngược lại in `NO`.",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 40,
                "solver": is_prime,
                "tests": [("7", "YES\n"), ("10", "NO\n"), ("97", "YES\n"), ("100", "NO\n"), ("101", "YES\n")]
            },
            {
                "topic": "Đếm số ước số nguyên dương",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng số lượng ước số của $N$.",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 40,
                "solver": count_divs,
                "tests": [("12", "6\n"), ("1", "1\n"), ("16", "5\n"), ("100", "9\n"), ("29", "2\n")]
            },
            {
                "topic": "Ước chung lớn nhất và Bội chung nhỏ nhất",
                "input_desc": "Một dòng chứa hai số nguyên dương $a, b$.",
                "output_desc": "In ra $\\gcd(a, b)$ và $\\text{lcm}(a, b)$ cách nhau một khoảng trắng.",
                "constraints": "$1 \\le a, b \\le 10^9$.",
                "pts": 40,
                "solver": gcd_lcm,
                "tests": [("12 18", "6 36\n"), ("7 13", "1 91\n"), ("24 60", "12 120\n"), ("100 25", "25 100\n"), ("8 8", "8 8\n")]
            },
            {
                "topic": "Kiểm tra số chính phương",
                "input_desc": "Một dòng chứa số nguyên không âm $N$.",
                "output_desc": "In `YES` nếu $N$ là số chính phương, ngược lại in `NO`.",
                "constraints": "$0 \\le N \\le 10^{14}$.",
                "pts": 40,
                "solver": is_sq,
                "tests": [("16", "YES\n"), ("15", "NO\n"), ("0", "YES\n"), ("10000", "YES\n"), ("2", "NO\n")]
            },
            {
                "topic": "Đếm chữ số 0 tận cùng của giai thừa N!",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra số chữ số 0 ở tận cùng của $N!$.",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 45,
                "solver": trailing_zeros,
                "tests": [("5", "1\n"), ("10", "2\n"), ("25", "6\n"), ("100", "24\n"), ("1000", "249\n")]
            },
            {
                "topic": "Tính tổng các chữ số của N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng các chữ số của $N$.",
                "constraints": "$1 \\le N \\le 10^{18}$.",
                "pts": 40,
                "solver": sum_digits,
                "tests": [("12345", "15\n"), ("999", "27\n"), ("1000", "1\n"), ("88", "16\n"), ("7", "7\n")]
            },
            {
                "topic": "Lũy thừa nhanh Modulo (A^B mod M)",
                "input_desc": "Một dòng chứa ba số nguyên $a, b, m$ ($m > 0$).",
                "output_desc": "In ra giá trị $a^b \\pmod m$.",
                "constraints": "$0 \\le a, b \\le 10^{18}, 1 \\le m \\le 10^9+7$.",
                "pts": 45,
                "solver": mod_exp,
                "tests": [("2 10 1000", "24\n"), ("3 5 7", "5\n"), ("2 0 10", "1\n"), ("5 3 100", "25\n"), ("10 6 1000000007", "1000000\n")]
            },
            {
                "topic": "Hàm số học phi Euler (Totient)",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra giá trị $\\phi(N)$ (số lượng số nguyên dương $\\le N$ nguyên tố cùng nhau với $N$).",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 50,
                "solver": phi,
                "tests": [("9", "6\n"), ("1", "1\n"), ("10", "4\n"), ("13", "12\n"), ("36", "12\n")]
            }
        ]

    elif prefix == "ds":
        def rsq_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, q = map(int, lines[0].split())
            arr = [int(x) for x in lines[1].split()]
            pref = [0] * (n + 1)
            for i in range(n): pref[i+1] = pref[i] + arr[i]
            res = []
            for line in lines[2:2+q]:
                l, r = map(int, line.split())
                res.append(str(pref[r] - pref[l-1]))
            return "\n".join(res) + "\n"

        def paren_solve(s):
            st = []
            m = {')': '(', ']': '[', '}': '{'}
            for c in s.strip():
                if c in '([{': st.append(c)
                elif c in ')]}':
                    if not st or st[-1] != m[c]: return "NO\n"
                    st.pop()
            return "YES\n" if not st else "NO\n"

        def queue_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            q = []
            for l in lines[1:]:
                parts = l.split()
                if parts[0] == "PUSH": q.append(parts[1])
                elif parts[0] == "POP":
                    if q: q.pop(0)
            front = q[0] if q else "EMPTY"
            return f"{front} {len(q)}\n"

        def sliding_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, k = map(int, lines[0].split())
            arr = [int(x) for x in lines[1].split()]
            res = []
            for i in range(n - k + 1):
                res.append(str(max(arr[i:i+k])))
            return " ".join(res) + "\n"

        def rmq_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, q = map(int, lines[0].split())
            arr = [int(x) for x in lines[1].split()]
            res = []
            for line in lines[2:2+q]:
                l, r = map(int, line.split())
                res.append(str(min(arr[l-1:r])))
            return "\n".join(res) + "\n"

        def freq_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, q = map(int, lines[0].split())
            arr = [int(x) for x in lines[1].split()]
            from collections import Counter
            counts = Counter(arr)
            queries = [int(x) for x in lines[2].split()]
            res = [str(counts[x]) for x in queries]
            return " ".join(res) + "\n"

        def stack_rev_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            arr = lines[1].split()
            return " ".join(reversed(arr)) + "\n"

        def diff_solve(s):
            lines = [x.strip() for x in s.strip().split("\n") if x.strip()]
            n, q = map(int, lines[0].split())
            diff = [0] * (n + 2)
            for l in lines[1:1+q]:
                left, right, val = map(int, l.split())
                diff[left] += val
                diff[right + 1] -= val
            cur = 0
            res = []
            for i in range(1, n + 1):
                cur += diff[i]
                res.append(str(cur))
            return " ".join(res) + "\n"

        return [
            {
                "topic": "Truy vấn tổng đoạn liên tiếp (Range Sum Query)",
                "input_desc": "Dòng 1: Hai số $N, Q$. Dòng 2: $N$ phần tử mảng. $Q$ dòng tiếp theo: mỗi dòng chứa hai chỉ số $L, R$ (1-based).",
                "output_desc": "In ra kết quả tổng đoạn $[L, R]$ trên từng dòng.",
                "constraints": "$1 \\le N, Q \\le 10^5, -10^4 \\le A_i \\le 10^4$.",
                "pts": 55,
                "solver": rsq_solve,
                "tests": [
                    ("5 2\n1 2 3 4 5\n1 3\n2 5", "6\n14\n"),
                    ("4 1\n10 20 30 40\n1 4", "100\n"),
                    ("6 2\n2 4 6 8 10 12\n2 4\n1 6", "18\n42\n"),
                    ("3 2\n5 5 5\n1 2\n2 3", "10\n10\n"),
                    ("5 1\n-1 -2 3 4 5\n1 5", "9\n")
                ]
            },
            {
                "topic": "Kiểm tra dấu ngoặc hợp lệ bằng Ngăn xếp (Stack)",
                "input_desc": "Một dòng duy nhất chứa chuỗi các ký tự dấu ngoặc `()`, `[]`, `{}`.",
                "output_desc": "In `YES` nếu dãy ngoặc hợp lệ, ngược lại in `NO`.",
                "constraints": "$1 \\le |S| \\le 10^5$.",
                "pts": 55,
                "solver": paren_solve,
                "tests": [("()[]{}", "YES\n"), ("([)]", "NO\n"), ("{[]}", "YES\n"), ("(", "NO\n"), (")(", "NO\n")]
            },
            {
                "topic": "Mô phỏng hàng đợi (Queue Simulation)",
                "input_desc": "Dòng 1: Số thao tác $K$. $K$ dòng tiếp: `PUSH X` hoặc `POP`.",
                "output_desc": "In ra phần tử ở đầu hàng đợi (`front`) và số lượng phần tử còn lại trong hàng đợi cách nhau bởi dấu cách. Nếu rỗng in `EMPTY 0`.",
                "constraints": "$1 \\le K \\le 10^5$.",
                "pts": 55,
                "solver": queue_solve,
                "tests": [
                    ("3\nPUSH 10\nPUSH 20\nPOP", "20 1\n"),
                    ("2\nPUSH 5\nPOP", "EMPTY 0\n"),
                    ("4\nPUSH 1\nPUSH 2\nPUSH 3\nPOP", "2 2\n"),
                    ("2\nPUSH 100\nPUSH 200", "100 2\n"),
                    ("1\nPOP", "EMPTY 0\n")
                ]
            },
            {
                "topic": "Giá trị lớn nhất trong cửa sổ trượt (Sliding Window Maximum)",
                "input_desc": "Dòng 1: Hai số $N$ và $K$ ($K \\le N$). Dòng 2: $N$ số nguyên của mảng.",
                "output_desc": "In ra giá trị lớn nhất trong từng cửa sổ kích thước $K$ từ trái sang phải.",
                "constraints": "$1 \\le K \\le N \\le 10^5$.",
                "pts": 60,
                "solver": sliding_solve,
                "tests": [
                    ("8 3\n1 3 -1 -3 5 3 6 7", "3 3 5 5 6 7\n"),
                    ("4 2\n1 2 3 4", "2 3 4\n"),
                    ("5 1\n5 4 3 2 1", "5 4 3 2 1\n"),
                    ("3 3\n10 20 30", "30\n"),
                    ("4 2\n10 -5 20 -2", "10 20 20\n")
                ]
            },
            {
                "topic": "Truy vấn giá trị nhỏ nhất trên đoạn (Range Minimum Query)",
                "input_desc": "Dòng 1: Hai số $N, Q$. Dòng 2: $N$ số nguyên mảng. $Q$ dòng tiếp theo chứa hai chỉ số $L, R$.",
                "output_desc": "In ra giá trị nhỏ nhất trong đoạn $[L, R]$ cho từng truy vấn.",
                "constraints": "$1 \\le N, Q \\le 10^5$.",
                "pts": 60,
                "solver": rmq_solve,
                "tests": [
                    ("5 2\n5 2 8 1 9\n1 3\n3 5", "2\n1\n"),
                    ("4 1\n4 3 2 1\n1 4", "1\n"),
                    ("3 2\n10 10 10\n1 2\n2 3", "10\n10\n"),
                    ("5 1\n-5 0 5 10 15\n1 5", "-5\n"),
                    ("4 2\n1 4 2 8\n2 3\n1 4", "2\n1\n")
                ]
            },
            {
                "topic": "Đếm tần suất phần tử bằng Bảng băm (Frequency Map)",
                "input_desc": "Dòng 1: Hai số $N, Q$. Dòng 2: $N$ số nguyên của mảng. Dòng 3: $Q$ giá trị cần truy vấn số lần xuất hiện.",
                "output_desc": "In ra $Q$ số nguyên cách nhau một khoảng trắng biểu thị số lần xuất hiện tương ứng.",
                "constraints": "$1 \\le N, Q \\le 10^5$.",
                "pts": 55,
                "solver": freq_solve,
                "tests": [
                    ("6 3\n1 2 2 3 3 3\n1 2 4", "1 2 0\n"),
                    ("4 2\n5 5 5 5\n5 1", "4 0\n"),
                    ("3 3\n1 2 3\n1 2 3", "1 1 1\n"),
                    ("5 1\n10 20 30 40 50\n30", "1\n"),
                    ("4 2\n-1 -1 2 2\n-1 0", "2 0\n")
                ]
            },
            {
                "topic": "Đảo ngược dãy số sử dụng Ngăn xếp (Stack Reverse)",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên cần đảo ngược.",
                "output_desc": "In ra dãy số sau khi lấy ra từ ngăn xếp.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 50,
                "solver": stack_rev_solve,
                "tests": [
                    ("5\n1 2 3 4 5", "5 4 3 2 1\n"),
                    ("3\n10 20 30", "30 20 10\n"),
                    ("1\n42", "42\n"),
                    ("4\n-1 -2 -3 -4", "-4 -3 -2 -1\n"),
                    ("2\n100 200", "200 100\n")
                ]
            },
            {
                "topic": "Cập nhật đoạn với Mảng hiệu (Difference Array)",
                "input_desc": "Dòng 1: Hai số $N, Q$. $Q$ dòng tiếp theo: mỗi dòng gồm $L, R, V$ (cộng giá trị $V$ vào đoạn $[L, R]$, mảng ban đầu toàn số 0).",
                "output_desc": "In ra $N$ phần tử của mảng sau khi hoàn thành tất cả các thao tác cập nhật.",
                "constraints": "$1 \\le N, Q \\le 10^5, -10^4 \\le V \\le 10^4$.",
                "pts": 60,
                "solver": diff_solve,
                "tests": [
                    ("5 2\n1 3 2\n2 4 3", "2 5 5 3 0\n"),
                    ("3 1\n1 3 5", "5 5 5\n"),
                    ("4 2\n1 2 1\n3 4 2", "1 1 2 2\n"),
                    ("5 1\n2 4 -1", "0 -1 -1 -1 0\n"),
                    ("2 2\n1 1 10\n2 2 20", "10 20\n")
                ]
            }
        ]

    elif prefix == "vt":
        return [
            {
                "topic": "Tìm giá trị lớn nhất và nhỏ nhất của mảng",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên $A_1, A_2, \\dots, A_N$.",
                "output_desc": "In ra giá trị lớn nhất và giá trị nhỏ nhất cách nhau một khoảng trắng.",
                "constraints": "$1 \\le N \\le 10^5, -10^9 \\le A_i \\le 10^9$.",
                "pts": 25,
                "solver": lambda s: f"{max([int(x) for x in s.strip().splitlines()[1].split()])} {min([int(x) for x in s.strip().splitlines()[1].split()])}\n",
                "tests": [("5\n1 4 2 8 5", "8 1\n"), ("6\n-2 5 0 -8 9 12", "12 -8\n"), ("4\n10 20 30 40", "40 10\n"), ("7\n3 1 4 1 5 9 2", "9 1\n"), ("5\n-5 -4 -3 -2 -1", "-1 -5\n")]
            },
            {
                "topic": "Tính tổng các phần tử trong mảng",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra tổng của toàn bộ các phần tử.",
                "constraints": "$1 \\le N \\le 10^5, -10^6 \\le A_i \\le 10^6$.",
                "pts": 25,
                "solver": lambda s: f"{sum([int(x) for x in s.strip().splitlines()[1].split()])}\n",
                "tests": [("5\n1 2 3 4 5", "15\n"), ("3\n10 20 30", "60\n"), ("4\n-1 1 -2 2", "0\n"), ("5\n100 200 300 400 500", "1500\n"), ("1\n42", "42\n")]
            },
            {
                "topic": "Đếm số phần tử dương trong mảng",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra số lượng phần tử strictly greater than 0.",
                "constraints": "$1 \\le N \\le 10^5, -10^9 \\le A_i \\le 10^9$.",
                "pts": 25,
                "solver": lambda s: f"{len([x for x in [int(x) for x in s.strip().splitlines()[1].split()] if x > 0])}\n",
                "tests": [("5\n1 -2 3 0 5", "3\n"), ("4\n-1 -2 -3 -4", "0\n"), ("4\n1 2 3 4", "4\n"), ("3\n0 0 0", "0\n"), ("5\n10 -5 20 -2 0", "2\n")]
            },
            {
                "topic": "In đảo ngược mảng một chiều",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra các phần tử theo thứ tự ngược lại, cách nhau một khoảng trắng.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: " ".join(str(x) for x in reversed([int(x) for x in s.strip().splitlines()[1].split()])) + "\n",
                "tests": [("5\n1 2 3 4 5", "5 4 3 2 1\n"), ("3\n10 20 30", "30 20 10\n"), ("1\n42", "42\n"), ("4\n4 3 2 1", "1 2 3 4\n"), ("2\n7 9", "9 7\n")]
            },
            {
                "topic": "Đếm số lần xuất hiện của phần tử X",
                "input_desc": "Dòng 1: Hai số $N$ và $X$. Dòng 2: $N$ số nguyên của mảng.",
                "output_desc": "In ra số lần xuất hiện của giá trị $X$ trong mảng.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{[int(x) for x in s.strip().splitlines()[1].split()].count(int(s.strip().splitlines()[0].split()[1]))}\n",
                "tests": [("5 2\n1 2 3 2 5", "2\n"), ("4 10\n1 2 3 4", "0\n"), ("3 7\n7 7 7", "3\n"), ("5 0\n0 1 0 2 0", "3\n"), ("1 4\n4", "1\n")]
            },
            {
                "topic": "Kiểm tra mảng đã sắp xếp tăng dần",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra `YES` nếu mảng đã được sắp xếp tăng dần, ngược lại in `NO`.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 30,
                "solver": lambda s: "YES\n" if [int(x) for x in s.strip().splitlines()[1].split()] == sorted([int(x) for x in s.strip().splitlines()[1].split()]) else "NO\n",
                "tests": [("5\n1 2 3 4 5", "YES\n"), ("5\n1 3 2 4 5", "NO\n"), ("3\n5 5 5", "YES\n"), ("4\n4 3 2 1", "NO\n"), ("1\n10", "YES\n")]
            },
            {
                "topic": "Tính trung bình cộng các phần tử",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra giá trị trung bình cộng làm tròn chính xác 2 chữ số thập phân.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 30,
                "solver": lambda s: f"{sum([int(x) for x in s.strip().splitlines()[1].split()]) / len([int(x) for x in s.strip().splitlines()[1].split()]):.2f}\n",
                "tests": [("4\n1 2 3 4", "2.50\n"), ("3\n10 20 30", "20.00\n"), ("5\n5 5 5 5 5", "5.00\n"), ("2\n7 8", "7.50\n"), ("1\n10", "10.00\n")]
            },
            {
                "topic": "Tính tổng các phần tử chẵn trong mảng",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra tổng các số chẵn trong mảng.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 30,
                "solver": lambda s: f"{sum([x for x in [int(x) for x in s.strip().splitlines()[1].split()] if x % 2 == 0])}\n",
                "tests": [("5\n1 2 3 4 5", "6\n"), ("4\n1 3 5 7", "0\n"), ("4\n2 4 6 8", "20\n"), ("3\n10 15 20", "30\n"), ("1\n8", "8\n")]
            }
        ]

    elif prefix == "vl":
        return [
            {
                "topic": "Tính tổng các số tự nhiên từ 1 đến N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng $S = 1 + 2 + \\dots + N$.",
                "constraints": "$1 \\le N \\le 10^8$.",
                "pts": 20,
                "solver": lambda s: f"{int(s.strip()) * (int(s.strip()) + 1) // 2}\n",
                "tests": [("5", "15\n"), ("10", "55\n"), ("50", "1275\n"), ("100", "5050\n"), ("500", "125250\n")]
            },
            {
                "topic": "Tính tổng bình phương các số từ 1 đến N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng $S = 1^2 + 2^2 + \\dots + N^2$.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 20,
                "solver": lambda s: f"{int(s.strip()) * (int(s.strip()) + 1) * (2 * int(s.strip()) + 1) // 6}\n",
                "tests": [("3", "14\n"), ("4", "30\n"), ("5", "55\n"), ("10", "385\n"), ("20", "2870\n")]
            },
            {
                "topic": "Tính tổng các số lẻ nhỏ hơn hoặc bằng N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng các số nguyên dương lẻ $\\le N$.",
                "constraints": "$1 \\le N \\le 10^6$.",
                "pts": 20,
                "solver": lambda s: f"{sum(x for x in range(1, int(s.strip()) + 1) if x % 2 == 1)}\n",
                "tests": [("5", "9\n"), ("10", "25\n"), ("7", "16\n"), ("1", "1\n"), ("20", "100\n")]
            },
            {
                "topic": "Tính tổng các số chẵn nhỏ hơn hoặc bằng N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng các số nguyên dương chẵn $\\le N$.",
                "constraints": "$1 \\le N \\le 10^6$.",
                "pts": 20,
                "solver": lambda s: f"{sum(x for x in range(1, int(s.strip()) + 1) if x % 2 == 0)}\n",
                "tests": [("5", "6\n"), ("10", "30\n"), ("6", "12\n"), ("2", "2\n"), ("20", "110\n")]
            },
            {
                "topic": "Tính giai thừa N! modulo 10^9+7",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra giá trị $N! \\pmod{10^9+7}$.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 25,
                "solver": lambda s: f"{__import__('math').factorial(int(s.strip())) % 1000000007}\n",
                "tests": [("5", "120\n"), ("3", "6\n"), ("1", "1\n"), ("6", "720\n"), ("10", "3628800\n")]
            },
            {
                "topic": "Đếm số ước nguyên dương của N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra số lượng ước số của $N$.",
                "constraints": "$1 \\le N \\le 10^6$.",
                "pts": 25,
                "solver": lambda s: f"{len([i for i in range(1, int(s.strip()) + 1) if int(s.strip()) % i == 0])}\n",
                "tests": [("6", "4\n"), ("12", "6\n"), ("7", "2\n"), ("16", "5\n"), ("1", "1\n")]
            },
            {
                "topic": "Đảo ngược các chữ số của N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra số nguyên nhận được sau khi đảo ngược các chữ số (loại bỏ các số 0 ở đầu nếu có).",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 25,
                "solver": lambda s: f"{int(s.strip()[::-1])}\n",
                "tests": [("12345", "54321\n"), ("100", "1\n"), ("7090", "907\n"), ("9", "9\n"), ("2026", "6202\n")]
            },
            {
                "topic": "Tính tổng các chữ số của N",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng các chữ số của $N$.",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 25,
                "solver": lambda s: f"{sum(int(c) for c in s.strip())}\n",
                "tests": [("123", "6\n"), ("9999", "36\n"), ("1000", "1\n"), ("456", "15\n"), ("7", "7\n")]
            }
        ]

    elif prefix == "srt":
        return [
            {
                "topic": "Sắp xếp mảng theo thứ tự tăng dần",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra các phần tử theo thứ tự tăng dần cách nhau một khoảng trắng.",
                "constraints": "$1 \\le N \\le 10^5, -10^9 \\le A_i \\le 10^9$.",
                "pts": 30,
                "solver": lambda s: " ".join(str(x) for x in sorted([int(x) for x in s.strip().splitlines()[1].split()])) + "\n",
                "tests": [("5\n5 2 8 1 9", "1 2 5 8 9\n"), ("4\n4 3 2 1", "1 2 3 4\n"), ("3\n9 0 -2", "-2 0 9\n"), ("5\n10 10 10 10 10", "10 10 10 10 10\n"), ("2\n5 1", "1 5\n")]
            },
            {
                "topic": "Sắp xếp mảng theo thứ tự giảm dần",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra các phần tử theo thứ tự giảm dần cách nhau một khoảng trắng.",
                "constraints": "$1 \\le N \\le 10^5, -10^9 \\le A_i \\le 10^9$.",
                "pts": 30,
                "solver": lambda s: " ".join(str(x) for x in sorted([int(x) for x in s.strip().splitlines()[1].split()], reverse=True)) + "\n",
                "tests": [("5\n1 2 3 4 5", "5 4 3 2 1\n"), ("4\n2 8 5 1", "8 5 2 1\n"), ("3\n-5 0 10", "10 0 -5\n"), ("2\n1 9", "9 1\n"), ("4\n7 7 3 3", "7 7 3 3\n")]
            },
            {
                "topic": "Tìm kiếm phần tử bằng Chặt nhị phân",
                "input_desc": "Dòng 1: Hai số $N$ và $X$. Dòng 2: $N$ số nguyên đã sắp xếp tăng dần.",
                "output_desc": "In `YES` nếu phần tử $X$ có mặt trong mảng, ngược lại in `NO`.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 30,
                "solver": lambda s: "YES\n" if int(s.strip().splitlines()[0].split()[1]) in set([int(x) for x in s.strip().splitlines()[1].split()]) else "NO\n",
                "tests": [("5 3\n1 2 3 4 5", "YES\n"), ("5 6\n1 2 3 4 5", "NO\n"), ("4 10\n5 10 15 20", "YES\n"), ("3 -1\n-5 -2 0", "NO\n"), ("1 7\n7", "YES\n")]
            },
            {
                "topic": "Tìm phần tử nhỏ thứ K trong mảng",
                "input_desc": "Dòng 1: Hai số $N$ và $K$ ($1 \\le K \\le N$). Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra giá trị của phần tử nhỏ thứ $K$ sau khi sắp xếp.",
                "constraints": "$1 \\le K \\le N \\le 10^5$.",
                "pts": 35,
                "solver": lambda s: f"{sorted([int(x) for x in s.strip().splitlines()[1].split()])[int(s.strip().splitlines()[0].split()[1]) - 1]}\n",
                "tests": [("5 3\n7 10 4 3 20", "7\n"), ("4 1\n9 2 8 5", "2\n"), ("4 4\n9 2 8 5", "9\n"), ("3 2\n1 2 3", "2\n"), ("5 2\n5 4 3 2 1", "2\n")]
            },
            {
                "topic": "Đếm số lượng giá trị phân biệt trong mảng",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra số lượng giá trị phân biệt (unique values).",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 35,
                "solver": lambda s: f"{len(set([int(x) for x in s.strip().splitlines()[1].split()]))}\n",
                "tests": [("5\n1 2 2 3 3", "3\n"), ("4\n5 5 5 5", "1\n"), ("4\n1 2 3 4", "4\n"), ("6\n10 20 10 20 30 10", "3\n"), ("1\n42", "1\n")]
            },
            {
                "topic": "Tìm cặp số có tổng bằng Target (Two Sum)",
                "input_desc": "Dòng 1: Hai số $N$ và $K$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In `YES` nếu tồn tại hai phần tử ở vị trí khác nhau có tổng bằng $K$, ngược lại in `NO`.",
                "constraints": "$2 \\le N \\le 10^5$.",
                "pts": 40,
                "solver": lambda s: (lambda nums, k: "YES\n" if any((k - x) in (nums[:i] + nums[i+1:]) for i, x in enumerate(nums)) else "NO\n")([int(x) for x in s.strip().splitlines()[1].split()], int(s.strip().splitlines()[0].split()[1])),
                "tests": [("4 9\n2 7 11 15", "YES\n"), ("3 6\n3 2 4", "YES\n"), ("2 6\n3 3", "YES\n"), ("4 10\n1 2 3 4", "NO\n"), ("3 5\n1 2 2", "NO\n")]
            },
            {
                "topic": "Tìm phần tử trung vị của mảng (Median)",
                "input_desc": "Dòng 1: Số nguyên $N$ (với $N$ là số lẻ). Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra phần tử trung vị của mảng.",
                "constraints": "$1 \\le N \\le 10^5$ ($N$ lẻ).",
                "pts": 35,
                "solver": lambda s: f"{sorted([int(x) for x in s.strip().splitlines()[1].split()])[len([int(x) for x in s.strip().splitlines()[1].split()]) // 2]}\n",
                "tests": [("5\n3 1 5 2 4", "3\n"), ("3\n10 50 20", "20\n"), ("1\n99", "99\n"), ("5\n9 1 8 2 7", "7\n"), ("3\n1 2 3", "2\n")]
            },
            {
                "topic": "Độ chênh lệch nhỏ nhất giữa hai phần tử bất kỳ",
                "input_desc": "Dòng 1: Số nguyên $N$. Dòng 2: $N$ số nguyên.",
                "output_desc": "In ra hiệu nhỏ nhất (không âm) giữa hai phần tử bất kỳ $|A_i - A_j|$ ($i \\ne j$).",
                "constraints": "$2 \\le N \\le 10^5$.",
                "pts": 40,
                "solver": lambda s: (lambda arr: f"{min(arr[i+1] - arr[i] for i in range(len(arr) - 1))}\n")(sorted([int(x) for x in s.strip().splitlines()[1].split()])),
                "tests": [("5\n1 5 3 19 18", "1\n"), ("4\n10 20 30 40", "10\n"), ("3\n1 10 100", "9\n"), ("3\n5 5 8", "0\n"), ("2\n4 9", "5\n")]
            }
        ]

    elif prefix == "mt":
        return [
            {
                "topic": "Tính tổng tất cả phần tử trong ma trận",
                "input_desc": "Dòng 1: Hai số $N, M$. $N$ dòng tiếp theo, mỗi dòng chứa $M$ số nguyên.",
                "output_desc": "In ra tổng giá trị của toàn bộ các phần tử trong ma trận.",
                "constraints": "$1 \\le N, M \\le 500$.",
                "pts": 30,
                "solver": lambda s: f"{sum(sum(int(x) for x in l.split()) for l in s.strip().splitlines()[1:])}\n",
                "tests": [("2 2\n1 2\n3 4", "10\n"), ("3 3\n1 2 3\n4 5 6\n7 8 9", "45\n"), ("2 3\n5 10 15\n20 25 30", "105\n"), ("3 2\n1 1\n2 2\n3 3", "12\n"), ("1 4\n2 4 6 8", "20\n")]
            },
            {
                "topic": "Tính tổng đường chéo chính ma trận vuông",
                "input_desc": "Dòng 1: Số nguyên $N$. $N$ dòng tiếp theo chứa ma trận $N \\times N$.",
                "output_desc": "In ra tổng các phần tử trên đường chéo chính $\\sum_{i=1}^N A_{i,i}$.",
                "constraints": "$1 \\le N \\le 500$.",
                "pts": 35,
                "solver": lambda s: f"{sum(int(s.strip().splitlines()[i+1].split()[i]) for i in range(int(s.strip().splitlines()[0])))}\n",
                "tests": [("3\n1 2 3\n4 5 6\n7 8 9", "15\n"), ("2\n10 20\n30 40", "50\n"), ("1\n42", "42\n"), ("3\n1 0 0\n0 1 0\n0 0 1", "3\n"), ("4\n1 2 3 4\n5 6 7 8\n9 1 2 3\n4 5 6 7", "16\n")]
            },
            {
                "topic": "Tính tổng các phần tử trên đường biên ma trận",
                "input_desc": "Dòng 1: Hai số $N, M$. $N$ dòng tiếp theo chứa ma trận $N \\times M$.",
                "output_desc": "In ra tổng các phần tử nằm trên 4 cạnh đường biên.",
                "constraints": "$1 \\le N, M \\le 500$.",
                "pts": 35,
                "solver": lambda s: (lambda n, m, g: f"{sum(g[i][j] for i in range(n) for j in range(m) if i == 0 or i == n - 1 or j == 0 or j == m - 1)}\n")(int(s.strip().splitlines()[0].split()[0]), int(s.strip().splitlines()[0].split()[1]), [[int(x) for x in l.split()] for l in s.strip().splitlines()[1:]]),
                "tests": [("3 3\n1 2 3\n4 5 6\n7 8 9", "40\n"), ("2 2\n1 1\n1 1", "4\n"), ("1 3\n2 4 6", "12\n"), ("3 1\n1\n2\n3", "6\n"), ("3 3\n1 1 1\n1 0 1\n1 1 1", "8\n")]
            },
            {
                "topic": "Tìm phần tử lớn nhất trong ma trận",
                "input_desc": "Dòng 1: Hai số $N, M$. $N$ dòng tiếp theo chứa ma trận $N \\times M$.",
                "output_desc": "In ra giá trị lớn nhất trong toàn bộ ma trận.",
                "constraints": "$1 \\le N, M \\le 500$.",
                "pts": 30,
                "solver": lambda s: f"{max(max(int(x) for x in l.split()) for l in s.strip().splitlines()[1:])}\n",
                "tests": [("2 3\n1 9 2\n8 3 7", "9\n"), ("3 3\n1 2 3\n4 5 6\n7 8 9", "9\n"), ("2 2\n-5 -2\n-8 -1", "-1\n"), ("1 1\n42", "42\n"), ("2 4\n10 20 30 40\n5 15 25 35", "40\n")]
            },
            {
                "topic": "Tìm hàng có tổng lớn nhất",
                "input_desc": "Dòng 1: Hai số $N, M$. $N$ dòng tiếp theo chứa ma trận $N \\times M$.",
                "output_desc": "In ra chỉ số hàng (1-based) có tổng các phần tử lớn nhất.",
                "constraints": "$1 \\le N, M \\le 500$.",
                "pts": 35,
                "solver": lambda s: f"{max(range(len(s.strip().splitlines()[1:])), key=lambda i: sum(int(x) for x in s.strip().splitlines()[i+1].split())) + 1}\n",
                "tests": [("3 3\n1 2 3\n4 5 6\n1 1 1", "2\n"), ("2 2\n10 20\n5 10", "1\n"), ("3 2\n1 1\n2 2\n3 3", "3\n"), ("1 3\n5 5 5", "1\n"), ("4 2\n1 0\n2 0\n3 0\n4 0", "4\n")]
            },
            {
                "topic": "Đếm số phần tử âm trong ma trận",
                "input_desc": "Dòng 1: Hai số $N, M$. $N$ dòng tiếp theo chứa ma trận $N \\times M$.",
                "output_desc": "In ra số lượng phần tử có giá trị âm (< 0).",
                "constraints": "$1 \\le N, M \\le 500$.",
                "pts": 30,
                "solver": lambda s: f"{sum(sum(1 for x in l.split() if int(x) < 0) for l in s.strip().splitlines()[1:])}\n",
                "tests": [("2 2\n-1 2\n3 -4", "2\n"), ("3 3\n1 2 3\n4 5 6\n7 8 9", "0\n"), ("2 2\n-5 -6\n-7 -8", "4\n"), ("1 3\n0 -2 5", "1\n"), ("3 1\n-1\n-2\n-3", "3\n")]
            },
            {
                "topic": "Kiểm tra ma trận đối xứng",
                "input_desc": "Dòng 1: Số nguyên $N$. $N$ dòng tiếp theo chứa ma trận vuông $N \\times N$.",
                "output_desc": "In `YES` nếu ma trận đối xứng qua đường chéo chính ($A_{i,j} = A_{j,i}$), ngược lại in `NO`.",
                "constraints": "$1 \\le N \\le 500$.",
                "pts": 35,
                "solver": lambda s: (lambda n, g: "YES\n" if all(g[i][j] == g[j][i] for i in range(n) for j in range(n)) else "NO\n")(int(s.strip().splitlines()[0]), [[int(x) for x in l.split()] for l in s.strip().splitlines()[1:]]),
                "tests": [("3\n1 2 3\n2 4 5\n3 5 6", "YES\n"), ("3\n1 2 3\n4 5 6\n7 8 9", "NO\n"), ("2\n5 7\n7 5", "YES\n"), ("1\n42", "YES\n"), ("2\n1 2\n3 4", "NO\n")]
            },
            {
                "topic": "Tính tổng đường chéo phụ ma trận vuông",
                "input_desc": "Dòng 1: Số nguyên $N$. $N$ dòng tiếp theo chứa ma trận $N \\times N$.",
                "output_desc": "In ra tổng các phần tử trên đường chéo phụ $\\sum_{i=1}^N A_{i, N - i + 1}$.",
                "constraints": "$1 \\le N \\le 500$.",
                "pts": 35,
                "solver": lambda s: f"{sum(int(s.strip().splitlines()[i+1].split()[int(s.strip().splitlines()[0]) - 1 - i]) for i in range(int(s.strip().splitlines()[0])))}\n",
                "tests": [("3\n1 2 3\n4 5 6\n7 8 9", "15\n"), ("2\n1 2\n3 4", "5\n"), ("1\n42", "42\n"), ("3\n0 0 1\n0 1 0\n1 0 0", "3\n"), ("4\n1 2 3 4\n5 6 7 8\n9 1 2 3\n4 5 6 7", "16\n")]
            }
        ]

    else: # fnc (Recursion & Combinations)
        def fibo_rec(s):
            n = int(s.strip())
            a, b = 0, 1
            for _ in range(n): a, b = b, (a + b) % 1000000007
            return f"{a}\n"

        def pow_rec(s):
            a, b = map(int, s.split())
            return f"{pow(a, b, 1000000007)}\n"

        def gcd_rec(s):
            a, b = map(int, s.split())
            import math
            return f"{math.gcd(a, b)}\n"

        def hanoi_rec(s):
            n = int(s.strip())
            return f"{pow(2, n, 1000000007) - 1}\n"

        def sum_dig_rec(s):
            n = int(s.strip())
            return f"{sum(int(c) for c in str(n))}\n"

        def subsets_rec(s):
            n = int(s.strip())
            return f"{pow(2, n, 1000000007)}\n"

        def tribo_rec(s):
            n = int(s.strip())
            if n == 0: return "0\n"
            if n in (1, 2): return "1\n"
            a, b, c = 0, 1, 1
            for _ in range(n - 2):
                a, b, c = b, c, (a + b + c) % 1000000007
            return f"{c}\n"

        def stairs_rec(s):
            n = int(s.strip())
            if n <= 1: return "1\n"
            if n == 2: return "2\n"
            a, b, c = 1, 1, 2
            for _ in range(n - 2):
                a, b, c = b, c, (a + b + c) % 1000000007
            return f"{c}\n"

        return [
            {
                "topic": "Tính số Fibonacci thứ N bằng Đệ quy",
                "input_desc": "Một dòng chứa số nguyên không âm $N$.",
                "output_desc": "In ra số Fibonacci $F_N \\pmod{10^9+7}$ ($F_0=0, F_1=1$).",
                "constraints": "$0 \\le N \\le 10^5$.",
                "pts": 35,
                "solver": fibo_rec,
                "tests": [("0", "0\n"), ("1", "1\n"), ("5", "5\n"), ("10", "55\n"), ("20", "6765\n")]
            },
            {
                "topic": "Tính lũy thừa nhanh A^B bằng Đệ quy",
                "input_desc": "Một dòng chứa hai số nguyên $a, b$.",
                "output_desc": "In ra $a^b \\pmod{10^9+7}$.",
                "constraints": "$0 \\le a \\le 10^9, 0 \\le b \\le 10^9$.",
                "pts": 35,
                "solver": pow_rec,
                "tests": [("2 10", "1024\n"), ("3 4", "81\n"), ("5 3", "125\n"), ("2 0", "1\n"), ("10 5", "100000\n")]
            },
            {
                "topic": "Tìm ước chung lớn nhất bằng thuật toán Euclid",
                "input_desc": "Một dòng chứa hai số nguyên dương $a, b$.",
                "output_desc": "In ra $\\gcd(a, b)$.",
                "constraints": "$1 \\le a, b \\le 10^9$.",
                "pts": 35,
                "solver": gcd_rec,
                "tests": [("12 18", "6\n"), ("25 15", "5\n"), ("7 13", "1\n"), ("100 20", "20\n"), ("8 8", "8\n")]
            },
            {
                "topic": "Số bước tối thiểu giải bài toán Tháp Hà Nội",
                "input_desc": "Một dòng chứa số lượng đĩa $N$.",
                "output_desc": "In ra số bước chuyển đĩa tối thiểu $2^N - 1 \\pmod{10^9+7}$.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 40,
                "solver": hanoi_rec,
                "tests": [("1", "1\n"), ("2", "3\n"), ("3", "7\n"), ("4", "15\n"), ("10", "1023\n")]
            },
            {
                "topic": "Tính tổng các chữ số bằng Đệ quy",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra tổng các chữ số của $N$.",
                "constraints": "$1 \\le N \\le 10^9$.",
                "pts": 35,
                "solver": sum_dig_rec,
                "tests": [("123", "6\n"), ("4567", "22\n"), ("1000", "1\n"), ("9999", "36\n"), ("8", "8\n")]
            },
            {
                "topic": "Đếm số tập hợp con của tập N phần tử",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra số lượng tập con $2^N \\pmod{10^9+7}$.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 40,
                "solver": subsets_rec,
                "tests": [("1", "2\n"), ("2", "4\n"), ("3", "8\n"), ("10", "1024\n"), ("20", "1048576\n")]
            },
            {
                "topic": "Dãy số Tribonacci bằng Đệ quy",
                "input_desc": "Một dòng chứa số nguyên không âm $N$.",
                "output_desc": "In ra số Tribonacci $T_N \\pmod{10^9+7}$ ($T_0=0, T_1=1, T_2=1, T_n = T_{n-1}+T_{n-2}+T_{n-3}$).",
                "constraints": "$0 \\le N \\le 10^5$.",
                "pts": 40,
                "solver": tribo_rec,
                "tests": [("0", "0\n"), ("1", "1\n"), ("2", "1\n"), ("3", "2\n"), ("4", "4\n")]
            },
            {
                "topic": "Số cách bước lên N bậc thang (bước 1, 2 hoặc 3 bậc)",
                "input_desc": "Một dòng chứa số nguyên dương $N$.",
                "output_desc": "In ra số cách bước lên bậc thứ $N$ modulo $10^9+7$.",
                "constraints": "$1 \\le N \\le 10^5$.",
                "pts": 45,
                "solver": stairs_rec,
                "tests": [("1", "1\n"), ("2", "2\n"), ("3", "4\n"), ("4", "7\n"), ("5", "13\n")]
            }
        ]

