"""test_engine.py - Kiểm thử engine.py (chịu trách nhiệm: Huỳnh Tiến Sơn).

Gồm hai nhóm:
  1) Golden: so với các "giá trị vàng" G1-G5 trong đặc tả 05.
  2) Properties: các tính chất toán học phải đúng với MỌI chuỗi.

Chạy (trong thư mục 03_Son_Engine_Verification):   python -m unittest discover -s tests -v
QUY TẮC: nếu test vàng không khớp thì SỬA ENGINE, KHÔNG sửa giá trị vàng.
"""
import os
import random
import sys
import unittest

# Cho phép import engine.py nằm ở thư mục cha của tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import simulate, ALGOS

# Chuỗi tham chiếu với k = 3
G1 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 0, 7, 0, 1]
# Chuỗi Belady
BEL = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
# Các giá trị k dùng trong thí nghiệm chính
KS = [3, 4, 5, 6, 7, 8, 10, 12]


def f(algo, refs, k):
    """Rút gọn: trả về số page fault."""
    return simulate(algo, refs, k)["faults"]


class Golden(unittest.TestCase):
    """Nhóm 1: giá trị vàng G1-G5 (phải khớp tuyệt đối)."""

    def test_g1(self):
        #k = 3: OPT = 9, FIFO = 15, LRU = 12
        self.assertEqual((f("OPT", G1, 3), f("FIFO", G1, 3), f("LRU", G1, 3)), (9, 15, 12))

    def test_g2_belady(self):
        # Số fault theo k = 1..6. FIFO tăng từ 9 (k=3) lên 10 (k=4): nghịch lý Belady.
        mong_doi = {"FIFO": [12, 12, 9, 10, 5, 5],
                    "LRU":  [12, 12, 10, 8, 5, 5],
                    "OPT":  [12, 9, 7, 6, 5, 5]}
        for algo, v in mong_doi.items():
            self.assertEqual([f(algo, BEL, k) for k in range(1, 7)], v, algo)

    def test_g3_sequential(self):
        # Quét tuần tự 20 trang, N = 1000: FIFO = LRU = 100% fault ở mọi k
        s = [i % 20 for i in range(1000)]
        for algo in ("FIFO", "LRU"):
            self.assertEqual([f(algo, s, k) for k in KS], [1000] * 8)
        self.assertEqual([f("OPT", s, k) for k in KS], [896, 844, 792, 740, 688, 636, 532, 428])

    def test_g4_loop(self):
        # Vòng lặp 8 trang: k < 8 thì FIFO = LRU = 1000 fault; k >= 8 chỉ còn 8 (compulsory)
        s = [i % 8 for i in range(1000)]
        for algo in ("FIFO", "LRU"):
            self.assertEqual([f(algo, s, k) for k in KS], [1000] * 5 + [8] * 3)
        self.assertEqual([f("OPT", s, k) for k in KS], [716, 574, 432, 290, 149, 8, 8, 8])

    def test_opt_tie_break(self):
        """Quy tắc hòa của OPT (đặc tả 05, mục 2): trang không bao giờ dùng lại = xa vô cùng,
        nếu nhiều trang cùng vô cùng thì loại trang có SỐ NHỎ NHẤT.
        Quy tắc này không làm đổi tổng số fault nên phải kiểm tra qua trang bị loại (trace)."""
        def nan_nhan(refs, k):
            trace = simulate("OPT", refs, k, record_trace=True)["trace"]
            return [s["evicted"] for s in trace if s["evicted"] is not None]

        self.assertEqual(nan_nhan([1, 2, 3, 4], 3), [1])       # 1, 2, 3 đều không dùng lại -> loại 1
        self.assertEqual(nan_nhan([7, 3, 5, 9], 3), [3])       # loại 3, không phải 5 hay 7
        self.assertEqual(nan_nhan([8, 2, 6, 4, 8], 3), [2])    # 8 còn được dùng; 2 và 6 không -> loại 2

    def test_g5(self):
        #LRU với k = 4 có đúng 4 fault
        self.assertEqual(f("LRU", [0, 1, 2, 3, 2, 1, 0, 3, 2, 3], 4), 4)


class Properties(unittest.TestCase):
    """Nhóm 2: tính chất phải đúng với mọi chuỗi."""

    def setUp(self):
        # 300 chuỗi ngẫu nhiên nhỏ (số trang 1..8, độ dài 1..40); seed cố định để lặp lại được
        rnd = random.Random(2024)
        self.cases = [[rnd.randrange(rnd.randint(1, 8)) for _ in range(rnd.randint(1, 40))]
                      for _ in range(300)]

    def test_opt_is_lower_bound(self):
        # OPT là tối ưu: không thuật toán nào ít fault hơn OPT
        for r in self.cases:
            for k in range(1, 7):
                o = f("OPT", r, k)
                self.assertLessEqual(o, f("FIFO", r, k))
                self.assertLessEqual(o, f("LRU", r, k))

    def test_basic_invariants(self):
        # hits + faults = n;  compulsory <= faults <= n;  k đủ lớn thì chỉ còn fault bắt buộc
        for r in self.cases:
            for algo in ALGOS:
                for k in range(1, 7):
                    x = simulate(algo, r, k)
                    self.assertEqual(x["hits"] + x["faults"], len(r))
                    self.assertTrue(x["compulsory"] <= x["faults"] <= len(r))
                    if k >= x["compulsory"]:
                        self.assertEqual(x["faults"], x["compulsory"])

    def test_stack_property(self):
        # Tính chất stack: với LRU và OPT, thêm frame thì số fault KHÔNG bao giờ tăng
        # (FIFO không có tính chất này: nghịch lý Belady)
        for r in self.cases:
            for algo in ("LRU", "OPT"):
                v = [f(algo, r, k) for k in range(1, 8)]
                self.assertEqual(v, sorted(v, reverse=True), (algo, r))

    def test_k1(self):
        # Chỉ có 1 frame: số fault = số lần đổi trang liên tiếp + 1
        for r in self.cases:
            mong_doi = 1 + sum(1 for i in range(1, len(r)) if r[i] != r[i - 1])
            for algo in ALGOS:
                self.assertEqual(f(algo, r, 1), mong_doi)

    def test_trace(self):
        # Trace phải nhất quán ở từng bước
        for r in self.cases[:100]:
            for algo in ALGOS:
                for k in (1, 3, 5):
                    for s in simulate(algo, r, k, record_trace=True)["trace"]:
                        self.assertLessEqual(len(s["frames"]), k)         # không vượt quá k frame
                        self.assertIn(s["page"], s["frames"])             # trang vừa truy cập đang ở trong frame
                        if s["evicted"] is not None:
                            self.assertNotIn(s["evicted"], s["frames"])   # trang bị loại không còn trong frame
                            self.assertFalse(s["hit"])                    # chỉ loại trang khi có fault

    def test_bad_input(self):
        # Đầu vào sai phải báo ValueError rõ ràng
        for sai in (("XYZ", [1], 3), ("FIFO", [1], 0), ("LRU", [1], -2), ("OPT", [1], 2.5)):
            with self.assertRaises(ValueError):
                simulate(*sai)


if __name__ == "__main__":
    unittest.main()

