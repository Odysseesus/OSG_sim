# Phần của Hiển – Thí nghiệm, dữ liệu, biểu đồ

## Cấu trúc
    osg_sim/
      engine.py              (Sơn giao – KHÔNG tự viết)
      engine_reference.py    (bản tham chiếu CHỈ để thử pipeline; số liệu từ nó KHÔNG dùng trong Report)
      patterns.py            (Hiển)  6 hàm sinh reference string
      run_experiments.py     (Hiển)  chạy thí nghiệm -> results/*.csv + tự kiểm tra
      make_charts.py         (Hiển)  F1–F8, T1–T3
      tests/test_patterns.py (Hiển)

## Lệnh
    python -m unittest discover -v               # test patterns
    python run_experiments.py --fake --quick     # thử khung (engine giả, số vô nghĩa)
    python run_experiments.py --ref              # thử với bản tham chiếu (chỉ kiểm pipeline)
    python run_experiments.py                    # CHẠY THẬT với engine.py của Sơn (CP2, CP3)
    python make_charts.py                        # F1–F8 + T1–T3
    python make_charts.py --slide                # F2, F4, F6, F7 bản slide-ready -> figures/slide/
    python make_charts.py --lang vi              # nhãn tiếng Việt (nếu Đạt chọn)

## Cách đọc cột
- fault_rate = faults / N (phân số 0–1; biểu đồ đổi sang %). hit_ratio = 1 − fault_rate.
- Pattern xác định (Sequential-20, Loop-8): seed = 0, runs = 1, std = 0.
- std_faults là độ lệch chuẩn MẪU (ddof = 1) trên 30 seed; thanh lỗi trong hình = std_faults / N × 100.
- mean_ratio_to_OPT = mean_faults(algo) / mean_faults(OPT) cùng (pattern, k).

## Ghi lúc DATA FREEZE (điền tay)
- Ngày giờ: ...      - Python: ...      - Seeds: 1..30      - Commit id: ...
