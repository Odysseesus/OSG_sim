"""make_charts.py - Nguyen Hung Hien
Ve F1..F7 (+F8 tuy chon) va bang T1..T3 tu results/*.csv. KHONG doi so lieu - chi trinh bay.
  python make_charts.py            # bo day du, 200 dpi
  python make_charts.py --slide    # ban "slide-ready" (chu to, it duong): F2, F4, F6, F7 -> figures/slide/
  python make_charts.py --lang vi  # nhan tieng Viet (mac dinh en - hoi Dat truoc khi ve!)
"""
import argparse, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG, TAB = (os.path.join(HERE, d) for d in ("results", "figures", "tables"))
COLORS = {"FIFO": "#1f77b4", "LRU": "#ff7f0e", "OPT": "#2ca02c"}   # xanh duong / cam / xanh la
MARKERS = {"FIFO": "o", "LRU": "s", "OPT": "^"}
ALGOS = ["FIFO", "LRU", "OPT"]
PATS = ["Sequential-20", "Loop-8", "Uniform-Random", "Locality-Phases", "Skewed-80/20"]
RANDOM_PATS = {"Uniform-Random", "Locality-Phases", "Skewed-80/20"}
N = 1000

TXT = {
    "en": {"x": "Number of frames (k)", "y": "Page fault rate (%)", "fig": "F", "err": "error bars = std over 30 seeds",
           "grp": "Page fault rate at k = 6", "bel_y": "Number of page faults", "bel_t": "Belady-string (12 references)",
           "ratio": "Ratio to OPT (faults / faults_OPT)"},
    "vi": {"x": "Số frame (k)", "y": "Tỉ lệ page fault (%)", "fig": "H", "err": "thanh lỗi = độ lệch chuẩn trên 30 seed",
           "grp": "Tỉ lệ page fault tại k = 6", "bel_y": "Số page fault", "bel_t": "Belady-string (12 tham chiếu)",
           "ratio": "Tỉ lệ so với OPT (faults / faults_OPT)"},
}


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def load():
    s = {}
    for r in read(os.path.join(RES, "summary.csv")):
        s[(r["pattern"], r["algo"], int(r["k"]))] = {
            "rate": float(r["mean_fault_rate"]) * 100, "std": float(r["std_faults"]) / N * 100,
            "mf": float(r["mean_faults"]), "sf": float(r["std_faults"]), "ratio": float(r["mean_ratio_to_OPT"]),
            "runs": int(r["runs"])}
    b = {(r["algo"], int(r["k"])): int(r["faults"]) for r in read(os.path.join(RES, "belady.csv"))}
    return s, b


def ks_of(s):
    return sorted({k for (_, _, k) in s})


def style(slide):
    plt.rcParams.update({"font.size": 16 if slide else 11, "axes.titlesize": 18 if slide else 12,
                         "axes.labelsize": 16 if slide else 11, "legend.fontsize": 14 if slide else 10,
                         "axes.grid": True, "grid.alpha": 0.3, "lines.linewidth": 2.8 if slide else 1.8})


def save(fig, name, outdir, slide=False):
    os.makedirs(outdir, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, name + ".png"), dpi=200)
    plt.close(fig)


def line_chart(s, pat, T, num, slide):
    fig, ax = plt.subplots(figsize=(8, 5) if not slide else (9, 5.5))
    ks = ks_of(s)
    for a in ALGOS:
        y = [s[(pat, a, k)]["rate"] for k in ks]
        if pat in RANDOM_PATS and not slide:
            ax.errorbar(ks, y, yerr=[s[(pat, a, k)]["std"] for k in ks], label=a, color=COLORS[a],
                        marker=MARKERS[a], capsize=3)
        else:
            ax.plot(ks, y, label=a, color=COLORS[a], marker=MARKERS[a])
    title = f"{T['fig']}{num}: {pat}"
    if pat in RANDOM_PATS and not slide:
        title += f"  ({T['err']})"
    ax.set(title=title, xlabel=T["x"], ylabel=T["y"], xticks=ks, ylim=(-3, 105))
    ax.legend(title="Algorithm" if T is TXT["en"] else "Thuật toán")
    return fig


def group_bar(s, T, k=6, slide=False):
    import numpy as np
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(PATS)); w = 0.26
    for i, a in enumerate(ALGOS):
        ax.bar(x + (i - 1) * w, [s[(p, a, k)]["rate"] for p in PATS], w, label=a, color=COLORS[a])
    ax.set(title=f"{T['fig']}6: {T['grp']}", ylabel=T["y"], ylim=(0, 108))
    ax.set_xticks(x); ax.set_xticklabels(PATS, rotation=12 if not slide else 0, fontsize=11 if slide else 10)
    ax.legend()
    return fig


def belady_chart(b, T, slide=False):
    fig, ax = plt.subplots(figsize=(8, 5))
    ks = range(1, 7)
    for a in ALGOS:
        ax.plot(ks, [b[(a, k)] for k in ks], label=a, color=COLORS[a], marker=MARKERS[a])
    ax.annotate("FIFO: 9 → 10", xy=(4, 10), xytext=(4.3, 11.2), arrowprops={"arrowstyle": "->"})
    ax.set(title=f"{T['fig']}7: {T['bel_t']}", xlabel=T["x"], ylabel=T["bel_y"], xticks=list(ks), ylim=(0, 13))
    ax.legend()
    return fig


def ratio_chart(s, T):
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.8), sharey=False)
    ks = ks_of(s)
    for ax, p in zip(axes, PATS):
        for a in ("FIFO", "LRU"):
            ax.plot(ks, [s[(p, a, k)]["ratio"] for k in ks], color=COLORS[a], marker=MARKERS[a], label=a)
        ax.axhline(1, color=COLORS["OPT"], ls="--", label="OPT = 1")
        ax.set(title=p, xlabel=T["x"], xticks=ks)
    axes[0].set_ylabel(T["ratio"]); axes[0].legend()
    fig.suptitle(f"{T['fig']}8: {T['ratio']}")
    return fig


def fmt(r, rand):
    return f"{r['rate']:.1f} ± {r['std']:.1f}" if rand else f"{r['rate']:.1f}"


def write_table(name, header, rows):
    os.makedirs(TAB, exist_ok=True)
    with open(os.path.join(TAB, name + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    with open(os.path.join(TAB, name + ".md"), "w") as f:
        f.write("| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n")
        for r in rows:
            f.write("| " + " | ".join(str(c) for c in r) + " |\n")


def tables(s, b):
    # T1: fault rate (%) tai k=4 va k=8, 5 pattern x 3 thuat toan (mean ± std)
    rows = [[p] + [fmt(s[(p, a, k)], p in RANDOM_PATS) for k in (4, 8) for a in ALGOS] for p in PATS]
    hdr = ["Pattern"] + [f"{a} (k={k})" for k in (4, 8) for a in ALGOS]
    write_table("T1_fault_rate_k4_k8", hdr, rows)
    # T2: Belady FIFO/LRU/OPT theo k = 1..6
    write_table("T2_belady", ["k"] + ALGOS, [[k] + [b[(a, k)] for a in ALGOS] for k in range(1, 7)])
    # T3: ratio_to_OPT tai k=6
    write_table("T3_ratio_to_OPT_k6", ["Pattern", "FIFO", "LRU", "OPT"],
                [[p] + [f"{s[(p, a, 6)]['ratio']:.2f}" for a in ALGOS] for p in PATS])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slide", action="store_true")
    ap.add_argument("--lang", default="en", choices=["en", "vi"])
    a = ap.parse_args()
    T = TXT[a.lang]
    s, b = load()
    style(a.slide)
    if a.slide:   # ban slide-ready: F2, F4, F6, F7
        out = os.path.join(FIG, "slide")
        save(line_chart(s, "Loop-8", T, 2, True), "F2_Loop-8", out)
        save(line_chart(s, "Locality-Phases", T, 4, True), "F4_Locality-Phases", out)
        save(group_bar(s, T, 6, True), "F6_grouped_k6", out)
        save(belady_chart(b, T, True), "F7_Belady", out)
        print("Da ve ban slide-ready ->", out); return
    names = ["Sequential-20", "Loop-8", "Uniform-Random", "Locality-Phases", "Skewed-80_20"]
    for i, p in enumerate(PATS, 1):
        save(line_chart(s, p, T, i, False), f"F{i}_{names[i-1]}", FIG)
    save(group_bar(s, T, 6), "F6_grouped_k6", FIG)
    save(belady_chart(b, T), "F7_Belady", FIG)
    save(ratio_chart(s, T), "F8_ratio_to_OPT", FIG)
    tables(s, b)
    print("Da ve F1-F8 ->", FIG, "| bang T1-T3 ->", TAB)


if __name__ == "__main__":
    main()
