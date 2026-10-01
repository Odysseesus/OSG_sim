"""patterns.py - Nguyen Hung Hien
Sinh reference string cho 6 access pattern (tham so DONG BANG theo 05_SIMULATOR_SPEC_CHUNG).
Moi ham tra ve list[int]. Ham ngau nhien dung random.Random(seed) RIENG (khong dung random toan cuc)
-> cung seed cho cung ket qua tren moi may.
"""
import random

N_DEFAULT = 1000   # N: do dai reference string
V_DEFAULT = 20     # V: so page ao (page 0..19)


def gen_sequential(n=N_DEFAULT, v=V_DEFAULT):
    """P1 Sequential-20: refs[i] = i mod 20. Quet lap toan bo khong gian, khong tai su dung
    trong khoang < 20 (truong hop xau cho FIFO/LRU khi k < 20). Xac dinh, khong seed."""
    return [i % v for i in range(n)]


def gen_loop(n=N_DEFAULT, length=8):
    """P2 Loop-8: refs[i] = i mod 8. Vong lap 8 page; diem chuyen pha ky vong tai k = 8."""
    return [i % length for i in range(n)]


def gen_uniform(n=N_DEFAULT, v=V_DEFAULT, seed=1):
    """P3 Uniform-Random: moi tham chieu chon deu trong 0..v-1 (khong co locality)."""
    rng = random.Random(seed)
    return [rng.randrange(v) for _ in range(n)]


def _locality(n, v, phases, phase_len, ws, p_in, seed):
    assert phases * phase_len == n, "phases * phase_len phai bang n"
    rng = random.Random(seed)
    refs, sets = [], []
    for _ in range(phases):
        wset = rng.sample(range(v), ws)            # 5 page KHONG lap cua pha nay
        sets.append(sorted(wset))
        for _ in range(phase_len):
            if rng.random() < p_in:                # 90%: chon deu trong working set
                refs.append(rng.choice(wset))
            else:                                  # 10%: chon deu trong toan bo 0..v-1
                refs.append(rng.randrange(v))
    return refs, sets


def gen_locality(n=N_DEFAULT, v=V_DEFAULT, phases=10, phase_len=100, ws=5, p_in=0.9, seed=1):
    """P4 Locality-Phases: 10 pha x 100 tham chieu, moi pha co working set 5 page.
    Lien he: locality of reference (Slide 80), working set (Textbook Sec 3.4.8)."""
    return _locality(n, v, phases, phase_len, ws, p_in, seed)[0]


def gen_locality_with_sets(n=N_DEFAULT, v=V_DEFAULT, phases=10, phase_len=100, ws=5, p_in=0.9, seed=1):
    """Giong gen_locality nhung tra them danh sach working set tung pha (dung cho test)."""
    return _locality(n, v, phases, phase_len, ws, p_in, seed)


def gen_skewed(n=N_DEFAULT, v=V_DEFAULT, hot=4, p_hot=0.8, seed=1):
    """P5 Skewed-80/20: page 0..3 (20% khong gian) nhan 80% tham chieu (deu trong 0..3);
    16 page con lai nhan 20% (deu). Khong doi theo thoi gian."""
    rng = random.Random(seed)
    refs = []
    for _ in range(n):
        if rng.random() < p_hot:
            refs.append(rng.randrange(hot))
        else:
            refs.append(hot + rng.randrange(v - hot))
    return refs


def belady_string():
    """P6 Belady-string (12 tham chieu). Nguon NGOAI textbook/slides:
    Belady, Nelson, Shedler (1969)."""
    return [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


# Ten pattern CO DINH (viet y het) -> ham sinh, va co can seed hay khong
PATTERNS = {
    "Sequential-20":   (gen_sequential, False),
    "Loop-8":          (gen_loop, False),
    "Uniform-Random":  (gen_uniform, True),
    "Locality-Phases": (gen_locality, True),
    "Skewed-80/20":    (gen_skewed, True),
}

