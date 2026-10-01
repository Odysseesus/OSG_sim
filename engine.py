"""engine.py - Lõi mô phỏng thay trang (chịu trách nhiệm: Huỳnh Tiến Sơn).

Engine nhận một chuỗi tham chiếu (reference string) và số frame k, rồi đếm số page fault
của một trong ba thuật toán: FIFO, LRU, OPT.

QUY ƯỚC :
  * Frame ban đầu RỖNG (demand paging: không nạp trước; Slide 81, Giáo trình Sec 3.4.8).
    Vì vậy các lần nạp trang đầu tiên CŨNG TÍNH là page fault (khớp Slide 66: OPT = 9).
  * FIFO : loại trang nạp sớm nhất (đầu hàng đợi).
    Truy cập trúng (HIT) KHÔNG làm thay đổi thứ tự.
  * LRU : loại trang lâu chưa được dùng nhất. LRU lý tưởng (không phải aging).
    Mỗi lần HIT hoặc nạp trang đều cập nhật trang đó thành "mới dùng gần nhất".
  * OPT : loại trang có lần dùng TIẾP THEO xa nhất trong tương lai.
    Trang không bao giờ được dùng lại coi như "xa vô cùng". Nếu nhiều trang cùng xa vô cùng
    thì loại trang có SỐ NHỎ NHẤT (để kết quả luôn xác định, chạy lần nào cũng như nhau).

KHÔNG mô hình hóa: bit R/M, ghi lại dirty page, TLB, nhiều tiến trình, thời gian I/O.
Mọi tham chiếu đều coi là truy cập đọc.
"""
from collections import OrderedDict, deque

# Danh sách thuật toán hợp lệ (tên viết đúng như đặc tả, không đổi giữa chừng)
ALGOS = ("FIFO", "LRU", "OPT")


def _next_use_table(refs):
    """Tính sẵn bảng "lần dùng tiếp theo" cho thuật toán OPT.

    Trả về danh sách nxt, trong đó nxt[i] là CHỈ SỐ của lần xuất hiện kế tiếp của trang refs[i]
    (sau vị trí i). Nếu trang đó không xuất hiện nữa thì nxt[i] = vô cùng.

    Cách làm: duyệt chuỗi từ CUỐI về ĐẦU, dùng dict `last` nhớ vị trí gần nhất đã gặp của mỗi trang.
    Nhờ vậy mỗi lần OPT chọn nạn nhân chỉ cần tra bảng, không phải quét lại phần còn lại của chuỗi.
    Ví dụ: refs = [1, 2, 1, 3]  ->  nxt = [2, vô cùng, vô cùng, vô cùng].
    """
    vo_cung = float("inf")
    nxt = [vo_cung] * len(refs)
    last = {}                                  # trang -> vị trí xuất hiện gần nhất (tính từ cuối)
    for i in range(len(refs) - 1, -1, -1):
        nxt[i] = last.get(refs[i], vo_cung)    # chưa gặp lần nào ở phía sau -> vô cùng
        last[refs[i]] = i
    return nxt


def simulate(algo, refs, k, record_trace=False):
    """Mô phỏng một thuật toán thay trang trên chuỗi tham chiếu `refs` với `k` frame.

    Tham số:
        algo         : "FIFO", "LRU" hoặc "OPT".
        refs         : danh sách số nguyên, mỗi số là một trang được truy cập.
        k            : số frame (số nguyên >= 1).
        record_trace : True -> ghi lại từng bước (dùng để vẽ bảng như Slide 68).

    Trả về dict gồm: algo, k, n (độ dài chuỗi), faults, hits, fault_rate, hit_ratio, compulsory;
    nếu record_trace=True thì có thêm "trace" (mỗi bước: step, page, hit, frames, evicted).
    Ràng buộc luôn đúng: hits + faults = n  và  compulsory <= faults <= n.
    """
    # --- Kiểm tra đầu vào, báo lỗi rõ ràng ---
    if algo not in ALGOS:
        raise ValueError(f"algo phải thuộc {ALGOS}, nhận được {algo!r}")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"k (số frame) phải là số nguyên >= 1, nhận được {k!r}")
    refs = list(refs)
    n = len(refs)

    faults = 0                 # đếm số page fault
    trace = []                 # nhật ký từng bước (chỉ dùng khi record_trace=True)

    # Mỗi thuật toán dùng một cấu trúc dữ liệu riêng để lưu các trang đang ở trong frame:
    queue = deque()            # FIFO : hàng đợi, đầu hàng = trang nạp sớm nhất
    lru = OrderedDict()        # LRU  : phần tử đầu = ít dùng nhất, phần tử cuối = mới dùng nhất
    opt = {}                   # OPT  : trang -> chỉ số lần dùng tiếp theo của nó
    nxt = _next_use_table(refs) if algo == "OPT" else None

    def dang_trong_frame():
        """Các trang hiện có trong frame (để ghi trace)."""
        if algo == "FIFO":
            return list(queue)
        if algo == "LRU":
            return list(lru)
        return sorted(opt)

    for i, p in enumerate(refs):
        evicted = None                         # trang bị loại ở bước này (nếu có)

        if algo == "FIFO":
            hit = p in queue
            if not hit:
                if len(queue) == k:            # frame đầy -> loại trang ở đầu hàng đợi
                    evicted = queue.popleft()
                queue.append(p)                # nạp trang mới vào cuối hàng
            # HIT: không làm gì cả (FIFO không đổi thứ tự khi trúng)

        elif algo == "LRU":
            hit = p in lru
            if hit:
                lru.move_to_end(p)             # HIT: đưa trang về cuối = "mới dùng gần nhất"
            else:
                if len(lru) == k:              # frame đầy -> loại trang ít dùng nhất (đầu danh sách)
                    evicted, _ = lru.popitem(last=False)
                lru[p] = True                  # nạp trang mới, đặt ở cuối

        else:  # OPT
            hit = p in opt
            if not hit and len(opt) == k:
                # Chọn trang có lần dùng tiếp theo XA NHẤT. Hòa (cùng vô cùng) -> trang số NHỎ NHẤT.
                # key=(xa nhất, -số trang): max ưu tiên xa nhất, rồi đến số trang nhỏ hơn.
                evicted = max(opt, key=lambda q: (opt[q], -q))
                del opt[evicted]
            opt[p] = nxt[i]                    # cập nhật lần dùng tiếp theo của p (cả khi HIT lẫn khi nạp)

        if not hit:
            faults += 1                        # truy cập trang không có trong frame = 1 page fault

        if record_trace:
            trace.append({"step": i, "page": p, "hit": hit,
                          "frames": dang_trong_frame(), "evicted": evicted})

    ket_qua = {
        "algo": algo, "k": k, "n": n,
        "faults": faults, "hits": n - faults,
        "fault_rate": faults / n if n else 0.0,        # không làm tròn, để nguyên số thực
        "hit_ratio": (n - faults) / n if n else 0.0,
        "compulsory": len(set(refs)),                  # số trang khác nhau = cận dưới của faults
    }
    if record_trace:
        ket_qua["trace"] = trace
    return ket_qua


def print_trace(algo, refs, k):
    """In bảng trace ra màn hình: mỗi cột là một bước, kèm F (fault) hoặc H (hit)."""
    t = simulate(algo, refs, k, record_trace=True)["trace"]
    w = max(2, max(len(str(p)) for p in refs) + 1)     # độ rộng mỗi cột
    print(f"{algo}, k={k}")
    print("ref  " + "".join(str(s["page"]).rjust(w) for s in t))
    for r in range(k):
        cells = [str(s["frames"][r]) if r < len(s["frames"]) else "." for s in t]
        print(f"f{r}   " + "".join(c.rjust(w) for c in cells))
    print("     " + "".join(("H" if s["hit"] else "F").rjust(w) for s in t))
    print("faults =", sum(not s["hit"] for s in t))

#test

if __name__ == "__main__":
    # Chạy trực tiếp file này sẽ in bảng trace.
    # Kết quả kỳ vọng: FIFO = 15, LRU = 12, OPT = 9 page fault.
    g1 = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 0, 7, 0, 1]
    for a in ALGOS:
        print_trace(a, g1, 3)
        print()
