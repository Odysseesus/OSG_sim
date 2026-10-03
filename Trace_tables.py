
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import os
from engine import simulate

G1 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 0, 7, 0, 1]   # Slide 66/68
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
OUT = os.path.join(ROOT, "outputs")


def fixed_slot_columns(algo, refs, k):
    """Return (columns, faults); column = (page, slots[list len k, None=empty], hit)."""
    slots, cols = [None] * k, []
    for s in simulate(algo, refs, k, record_trace=True)["trace"]:
        if not s["hit"]:
            idx = slots.index(None) if s["evicted"] is None else slots.index(s["evicted"])
            slots[idx] = s["page"]
        cols.append((s["page"], list(slots), s["hit"]))
    return cols, sum(1 for c in cols if not c[2])


def to_markdown(algo, refs, k):
    cols, faults = fixed_slot_columns(algo, refs, k)
    head = "| | " + " | ".join(str(c[0]) for c in cols) + " |"
    sep = "|---" * (len(cols) + 1) + "|"
    rows = [f"| Frame {r} | " + " | ".join("" if c[1][r] is None else str(c[1][r]) for c in cols) + " |"
            for r in range(k)]
    flag = "| Result | " + " | ".join("H" if c[2] else "F" for c in cols) + " |"
    return f"**{algo}, k = {k}: {faults} page faults**\n\n" + "\n".join([head, sep] + rows + [flag]) + "\n"


def to_text(algo, refs, k):
    cols, faults = fixed_slot_columns(algo, refs, k)
    out = [f"{algo}, k={k}", "ref    " + " ".join(f"{c[0]:>2}" for c in cols)]
    for r in range(k):
        out.append(f"frame{r} " + " ".join(f"{'.' if c[1][r] is None else c[1][r]:>2}" for c in cols))
    out.append("       " + " ".join(f"{'H' if c[2] else 'F':>2}" for c in cols))
    out.append(f"faults = {faults}")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "trace_G1.md"), "w", encoding="utf-8") as f:
        f.write("# Trace of the Slide 66/68 example (k = 3)\n\n")
        for a in ("FIFO", "LRU", "OPT"):
            f.write(to_markdown(a, G1, 3) + "\n")
    with open(os.path.join(OUT, "trace_belady.md"), "w", encoding="utf-8") as f:
        f.write("# Belady's anomaly: FIFO on 1 2 3 4 1 2 5 1 2 3 4 5\n\n")
        for k in (3, 4):
            f.write(to_markdown("FIFO", BELADY, k) + "\n")
    for a in ("FIFO", "LRU", "OPT"):
        print(to_text(a, G1, 3)); print()
    for k in (3, 4):
        print(to_text("FIFO", BELADY, k)); print()
    print("Wrote outputs/trace_G1.md and outputs/trace_belady.md")
