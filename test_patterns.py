import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import patterns as P


class TestPatterns(unittest.TestCase):
    def test_length_and_range(self):
        for refs in (P.gen_sequential(), P.gen_loop(), P.gen_uniform(seed=1),
                     P.gen_locality(seed=1), P.gen_skewed(seed=1)):
            self.assertEqual(len(refs), 1000)
            self.assertTrue(all(0 <= p <= 19 for p in refs))
        self.assertEqual(len(P.belady_string()), 12)

    def test_formula(self):
        self.assertEqual(P.gen_sequential(), [i % 20 for i in range(1000)])
        self.assertEqual(P.gen_loop(), [i % 8 for i in range(1000)])
        self.assertEqual(P.belady_string(), [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5])

    def test_seed_reproducible(self):
        for g in (P.gen_uniform, P.gen_locality, P.gen_skewed):
            self.assertEqual(g(seed=7), g(seed=7))
            self.assertNotEqual(g(seed=7), g(seed=8))

    def test_locality_in_phase(self):
        # moi pha >= 80% tham chieu thuoc working set; ky vong ~ 92.5%
        fracs = []
        for seed in range(1, 31):
            refs, sets = P.gen_locality_with_sets(seed=seed)
            for ph in range(10):
                chunk = refs[ph * 100:(ph + 1) * 100]
                self.assertEqual(len(sets[ph]), 5)
                self.assertEqual(len(set(sets[ph])), 5)       # 5 page khong lap
                f = sum(p in sets[ph] for p in chunk) / 100
                self.assertGreaterEqual(f, 0.80)
                fracs.append(f)
        self.assertAlmostEqual(sum(fracs) / len(fracs), 0.925, delta=0.01)

    def test_skewed_ratio(self):
        r = []
        for seed in range(1, 31):
            refs = P.gen_skewed(seed=seed)
            r.append(sum(p < 4 for p in refs) / len(refs))
        self.assertAlmostEqual(sum(r) / len(r), 0.80, delta=0.01)


if __name__ == "__main__":
    unittest.main()

