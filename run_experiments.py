"""run_experiments.py - Nguyen Hung Hien
Chay toan bo thi nghiem theo 05_SIMULATOR_SPEC_CHUNG (muc 3-4).
  python run_experiments.py --quick   # chay thu pattern xac dinh + 1 seed (kiem tra nhanh)
  python run_experiments.py --fake    # engine GIA (faults=0) de thu khung khi chua co engine
  python run_experiments.py           # chay DAY DU -> results/raw.csv, summary.csv, belady.csv
Thu tu vong lap: pattern -> k -> algo -> seed.
Engine: dung engine.py (Son) neu co; neu khong thi bao loi (hoac dung --ref de dung ban tham chieu).
"""
import argparse, csv, os, statistics, sys, time
from collections import defaultdict

import patterns as P

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
KS = [3, 4, 5, 6, 7, 8, 10, 12]
ALGOS = ["FIFO", "LRU", "OPT"]
SEEDS = range(1, 31)
RAW_COLS = ["pattern", "algo", "k", "seed", "n", "faults", "hits", "fault_rate", "hit_ratio", "compulsory"]
SUM_COLS = ["pattern", "algo", "k", "runs", "mean_faults", "std_faults", "mean_fault_rate", "mean_ratio_to_OPT"]


def load_engine(use_fake=False, use_ref=False):
    if use_fake:
        def fake(algo, refs, k, record_trace=False):
            n = len(refs)
            return {"algo": algo, "k": k, "n": n, "faults": 0, "hits": n, "fault_rate": 0.0,
                    "hit_ratio": 1.0, "compulsory": len(set(refs))}
        print("[!] DANG DUNG ENGINE GIA - ket qua KHONG co gia tri")
        return fake
    if not use_ref:
        try:
            from engine import simulate
            print("[ok] Dung engine.py cua Son")
            return simulate
        except ImportError:
            sys.exit("Khong tim thay engine.py. Cho Son giao, hoac chay voi --fake / --ref.")
    from engine_reference import simulate
    print("[!] Dang dung engine_reference.py (ban tham chieu) - chi de thu pipeline")
    return simulate


def run_all(simulate, quick=False):
    os.makedirs(RES, exist_ok=True)
    rows = []
    t0 = time.time()
    for name, (gen, needs_seed) in P.PATTERNS.items():
        seeds = ([1] if quick else list(SEEDS)) if needs_seed else [0]   # xac dinh: seed = 0
        for seed in seeds:
            refs = gen(seed=seed) if needs_seed else gen()
            for k in KS:
                for algo in ALGOS:
                    r = simulate(algo, refs, k)
                    rows.append({"pattern": name, "algo": algo, "k": k, "seed": seed,
                                 "n": r["n"], "faults": r["faults"], "hits": r["hits"],
                                 "fault_rate": r["fault_rate"], "hit_ratio": r["hit_ratio"],
                                 "compulsory": r["compulsory"]})
        print(f"  xong {name:16s} ({len(rows)} dong, {time.time()-t0:.1f}s)")
    return rows


def write_csv(path, cols, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def aggregate(rows):
    """raw -> summary: mean, std (mau, ddof=1), ratio_to_OPT. Pattern xac dinh: runs=1, std=0."""
    g = defaultdict(list)
    for r in rows:
        g[(r["pattern"], r["algo"], r["k"])].append(r)
    out = []
    for (pat, algo, k), rs in g.items():
        f = [x["faults"] for x in rs]
        mean_f = statistics.mean(f)
        std_f = statistics.stdev(f) if len(f) > 1 else 0.0
        opt = statistics.mean([x["faults"] for x in g[(pat, "OPT", k)]])
        out.append({"pattern": pat, "algo": algo, "k": k, "runs": len(rs),
                    "mean_faults": round(mean_f, 4), "std_faults": round(std_f, 4),
                    "mean_fault_rate": round(statistics.mean([x["fault_rate"] for x in rs]), 6),
                    "mean_ratio_to_OPT": round(mean_f / opt, 4) if opt else 1.0})
    order = {p: i for i, p in enumerate(P.PATTERNS)}
    out.sort(key=lambda r: (order[r["pattern"]], r["k"], ALGOS.index(r["algo"])))
    return out


def run_belady(simulate):
    refs = P.belady_string()
    return [{"algo": a, "k": k, "faults": simulate(a, refs, k)["faults"]}
            for a in ALGOS for k in range(1, 7)]


def check(raw, summ, belady, quick=False):
    ok = True
    if not quick:
        exp_rand, exp_det = 3 * 8 * 3 * 30, 2 * 8 * 3
        print(f"[check] raw.csv: {len(raw)} dong (ky vong {exp_rand}+{exp_det}={exp_rand+exp_det})")
        ok &= len(raw) == exp_rand + exp_det
        print(f"[check] belady.csv: {len(belady)} dong (ky vong 18)")
        ok &= len(belady) == 18
    # tinh chat tren MOI dong raw: hits+faults=N, compulsory<=faults<=N
    bad = [r for r in raw if r["hits"] + r["faults"] != r["n"] or not (r["compulsory"] <= r["faults"] <= r["n"])]
    print(f"[check] vi pham hits+faults=N hoac compulsory<=faults<=N: {len(bad)}")
    ok &= not bad
    # OPT <= FIFO, OPT <= LRU o MOI dong summary
    idx = {(s["pattern"], s["algo"], s["k"]): s["mean_faults"] for s in summ}
    viol = [(p, k) for (p, a, k), v in idx.items() if a != "OPT" and idx[(p, "OPT", k)] > v + 1e-9]
    print(f"[check] vi pham OPT <= FIFO/LRU (summary): {len(viol)} {viol[:3]}")
    ok &= not viol
    # OPT <= tung thuat toan o MOI (pattern,k,seed)
    byrun = {(r["pattern"], r["algo"], r["k"], r["seed"]): r["faults"] for r in raw}
    viol2 = [key for key, v in byrun.items() if key[1] != "OPT" and byrun[(key[0], "OPT", key[2], key[3])] > v]
    print(f"[check] vi pham OPT <= FIFO/LRU (tung seed): {len(viol2)}")
    ok &= not viol2
    # LRU/OPT khong tang khi k tang (tinh chat stack)
    for algo in ("LRU", "OPT"):
        for pat in P.PATTERNS:
            seq = [idx[(pat, algo, k)] for k in KS]
            if any(b > a + 1e-9 for a, b in zip(seq, seq[1:])):
                print(f"[check] LOI stack: {algo} tang khi k tang o {pat}: {seq}"); ok = False
    # G3 / G4 (bat buoc khop tung so)
    G3 = dict(zip([3, 4, 5, 6, 7, 8, 10, 12], [896, 844, 792, 740, 688, 636, 532, 428]))
    G4 = dict(zip([3, 4, 5, 6, 7], [716, 574, 432, 290, 149]))
    for k in KS:
        for a in ("FIFO", "LRU"):
            ok &= idx[("Sequential-20", a, k)] == 1000
        ok &= idx[("Sequential-20", "OPT", k)] == G3[k]
    for k in KS:
        if k <= 7:
            ok &= idx[("Loop-8", "FIFO", k)] == 1000 and idx[("Loop-8", "LRU", k)] == 1000
            ok &= idx[("Loop-8", "OPT", k)] == G4[k]
        else:
            ok &= all(idx[("Loop-8", a, k)] == 8 for a in ALGOS)
    print(f"[check] G3 (Sequential-20) + G4 (Loop-8) khop: {ok}")
    # G2 Belady
    b = {(r["algo"], r["k"]): r["faults"] for r in belady}
    G2 = {"FIFO": [12, 12, 9, 10, 5, 5], "LRU": [12, 12, 10, 8, 5, 5], "OPT": [12, 9, 7, 6, 5, 5]}
    g2_ok = all([b[(a, k)] for k in range(1, 7)] == G2[a] for a in ALGOS)
    print(f"[check] G2 (Belady-string) khop: {g2_ok}")
    ok &= g2_ok
    # Ky vong Uniform-Random: hit_ratio FIFO/LRU ~ k/V (lech > 5 diem % -> nghi loi)
    for a in ("FIFO", "LRU"):
        for k in (4, 10):
            hit = 1 - idx[("Uniform-Random", a, k)] / 1000
            flag = "ok" if abs(hit - k / 20) <= 0.05 else "NGHI LOI"
            print(f"[check] Uniform-Random {a} k={k}: hit={hit:.3f} (k/V={k/20:.2f}) {flag}")
            ok &= flag == "ok"
    print("[KET QUA]", "TAT CA DAT" if ok else "CO LOI - bao Son, KHONG freeze")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--ref", action="store_true", help="dung engine_reference.py")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    sim = load_engine(a.fake, a.ref)
    raw = run_all(sim, a.quick)
    summ = aggregate(raw)
    bel = run_belady(sim)
    write_csv(os.path.join(RES, "raw.csv"), RAW_COLS, raw)
    write_csv(os.path.join(RES, "summary.csv"), SUM_COLS, summ)
    write_csv(os.path.join(RES, "belady.csv"), ["algo", "k", "faults"], bel)
    print(f"Da ghi {len(raw)} / {len(summ)} / {len(bel)} dong vao results/")
    if not a.fake:
        check(raw, summ, bel, a.quick)


if __name__ == "__main__":
    main()

