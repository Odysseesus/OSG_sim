"""engine.py - Core page-replacement engine (owner: Huynh Tien Son).

Semantics follow 05_SIMULATOR_SPEC_CHUNG.txt section 2:
  * frames start EMPTY (demand paging; Slide 81, Textbook Sec 3.4.8), so cold-start
    loads count as faults (matches Slide 66: OPT = 9);
  * FIFO (Slide 68, Sec 3.4.3): evict head of queue; a HIT does NOT reorder;
  * LRU  (Slides 72-74, Sec 3.4.6): ideal LRU; every HIT/load -> most recently used;
  * OPT  (Slides 65-66, Sec 3.4.1): evict page whose next use is farthest in the future;
    never used again = infinity; ties -> smallest page number (deterministic).
Not modelled: R/M bits, dirty write-back, TLB, multi-process, I/O time.
"""
from collections import OrderedDict, deque

ALGOS = ("FIFO", "LRU", "OPT")


def _next_use_table(refs):
    """next_use[i] = index of the next occurrence of refs[i] after i (or infinity)."""
    inf = float("inf")
    nxt, last = [inf] * len(refs), {}
    for i in range(len(refs) - 1, -1, -1):
        nxt[i] = last.get(refs[i], inf)
        last[refs[i]] = i
    return nxt


def simulate(algo, refs, k, record_trace=False):
    if algo not in ALGOS:
        raise ValueError(f"algo must be one of {ALGOS}, got {algo!r}")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"k (number of frames) must be an int >= 1, got {k!r}")
    refs = list(refs)
    n = len(refs)

    faults = 0
    trace = []
    queue = deque()          # FIFO order (head = oldest)
    lru = OrderedDict()      # LRU order (first = least recently used)
    opt = {}                 # OPT: page -> index of its next use
    nxt = _next_use_table(refs) if algo == "OPT" else None

    def resident():
        return list(queue) if algo == "FIFO" else (list(lru) if algo == "LRU" else sorted(opt))

    for i, p in enumerate(refs):
        evicted = None
        if algo == "FIFO":
            hit = p in queue
            if not hit:
                if len(queue) == k:
                    evicted = queue.popleft()
                queue.append(p)
        elif algo == "LRU":
            hit = p in lru
            if hit:
                lru.move_to_end(p)
            else:
                if len(lru) == k:
                    evicted, _ = lru.popitem(last=False)
                lru[p] = True
        else:  # OPT
            hit = p in opt
            if not hit and len(opt) == k:
                # farthest next use; tie (all inf) -> smallest page number
                evicted = max(opt, key=lambda q: (opt[q], -q))
                del opt[evicted]
            opt[p] = nxt[i]          # refresh next-use of p (on hit or load)
        if not hit:
            faults += 1
        if record_trace:
            trace.append({"step": i, "page": p, "hit": hit,
                          "frames": resident(), "evicted": evicted})

    result = {
        "algo": algo, "k": k, "n": n, "faults": faults, "hits": n - faults,
        "fault_rate": faults / n if n else 0.0,
        "hit_ratio": (n - faults) / n if n else 0.0,
        "compulsory": len(set(refs)),
    }
    if record_trace:
        result["trace"] = trace
    return result


def print_trace(algo, refs, k):
    """Slide-68 style table: one column per step, frames + F/H marks."""
    t = simulate(algo, refs, k, record_trace=True)["trace"]
    w = max(2, max(len(str(p)) for p in refs) + 1)
    print(f"{algo}, k={k}")
    print("ref  " + "".join(str(s['page']).rjust(w) for s in t))
    for r in range(k):
        cells = [str(s["frames"][r]) if r < len(s["frames"]) else "." for s in t]
        print(f"f{r}   " + "".join(c.rjust(w) for c in cells))
    print("     " + "".join(("H" if s["hit"] else "F").rjust(w) for s in t))
    print("faults =", sum(not s["hit"] for s in t))


if __name__ == "__main__":
    g1 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 0, 7, 0, 1]
    for a in ALGOS:
        print_trace(a, g1, 3)
        print()
