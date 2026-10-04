# Phần của Hiển – Thí nghiệm, dữ liệu, biểu đồ

## Lệnh
    python -m unittest discover -v               # test patterns
    python run_experiments.py --fake --quick     # thử khung (engine giả, số vô nghĩa)
    python run_experiments.py --ref              # thử với bản tham chiếu (chỉ kiểm pipeline)
    python run_experiments.py                    # CHẠY THẬT với engine.py của Sơn (CP2, CP3)
    python make_charts.py                        # F1–F8 + T1–T3
    python make_charts.py --slide                # F2, F4, F6, F7 bản slide-ready -> figures/slide/
    python make_charts.py --lang vi              # nhãn tiếng Việt (nếu Đạt chọn)

## Tham số thí nghiệm
- N = 1000 tham chiếu, V = 20 page ảo (0..19), k ∈ {3,4,5,6,7,8,10,12}
- Frame ban đầu rỗng: các lần nạp đầu cũng tính là fault
- 5 pattern: Sequential-20, Loop-8 (xác định); Uniform-Random,
  Locality-Phases, Skewed-80/20 (ngẫu nhiên, 30 seed)
- Belady-string: chuỗi 12 tham chiếu, chạy riêng với k = 1..6

## Cột trong CSV (results/)
- raw.csv (2208 dòng, mỗi dòng 1 lần chạy): pattern, algo, k, seed, n, faults,
  hits, fault_rate, hit_ratio, compulsory
  - fault_rate = faults / n (phân số 0–1, KHÔNG phải %); hit_ratio = 1 − fault_rate
  - seed = 0 với pattern xác định (chỉ chạy 1 lần)
  - compulsory = số page khác nhau trong chuỗi (cận dưới của faults)
- summary.csv (120 dòng, đã tổng hợp theo pattern, algo, k): runs, mean_faults,
  std_faults, mean_fault_rate, mean_ratio_to_OPT
  - std_faults = độ lệch chuẩn mẫu (ddof = 1) trên 30 seed; = 0 với pattern xác định
  - mean_ratio_to_OPT = mean_faults(algo) / mean_faults(OPT) cùng pattern, k
- belady.csv (18 dòng): algo, k, faults

## Hình (figures/)
- F1–F5: tỉ lệ page fault (%) theo k, mỗi pattern một hình (thanh lỗi = std/1000×100)
- F6: so sánh 3 thuật toán trên 5 pattern tại k = 6
- F7: Belady-string (FIFO 9 → 10 khi k = 3 → 4)
- F8: tỉ lệ fault so với OPT
- Màu cố định: FIFO xanh dương, LRU cam, OPT xanh lá

## Bảng (tables/)
- T1: fault rate (%) tại k = 4 và k = 8, định dạng mean ± std
- T2: số fault của Belady-string theo k = 1..6
- T3: ratio_to_OPT tại k = 6
