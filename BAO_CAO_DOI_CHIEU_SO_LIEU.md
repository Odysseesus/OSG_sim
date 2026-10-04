# Báo cáo đối chiếu sản phẩm của Hiển (do Sơn kiểm soát số liệu)

Đối tượng kiểm tra: `patterns.py`, `run_experiments.py`, `make_charts.py`, `raw.csv`, `summary.csv`, `belady.csv`, `T1`, `T2`, `T3` (cả `.csv` và `.md`) do Hiển gửi.

## 1. Kết luận

**Số liệu của Hiển chính xác.** Không có số nào sai. Có 4 điểm cần sửa trong code và định dạng file (mục 3); các điểm này **không làm đổi con số nào**.

| Hạng mục | Cách kiểm tra | Kết quả |
|---|---|---|
| `raw.csv`, 2208 dòng | Sinh lại từng chuỗi bằng `patterns.py` + đúng seed, rồi tính bằng **hai bộ mô phỏng**: `engine.py` của Sơn và một bộ **độc lập viết kiểu khác** (danh sách thuần, không dùng `OrderedDict`/`deque`) | **2208/2208 dòng trùng** faults, hits, compulsory ở cả hai bộ |
| Lưới thí nghiệm | So với tập (pattern, thuật toán, k, seed) kỳ vọng | Không thiếu, không thừa, không trùng dòng nào |
| Ràng buộc từng dòng | N=1000; hits+faults=N; compulsory ≤ faults ≤ N; fault_rate = faults/N | Đạt cả 2208 dòng |
| OPT ≤ FIFO và OPT ≤ LRU | Mọi cặp (pattern, k, seed) | Không vi phạm |
| `summary.csv`, 120 dòng | Tính lại mean, std mẫu (n-1), rate, ratio_to_OPT, runs từ `raw.csv` | Đúng; sai lệch chỉ do làm tròn (lớn nhất: mean 3,3e-5; std 4,8e-5; ratio 4,9e-5) |
| `belady.csv`, 18 dòng | Hai bộ mô phỏng + giá trị vàng G2 | Đúng; FIFO k=3 → 9, k=4 → 10 |
| Giá trị vàng G3 (Sequential-20), G4 (Loop-8) | So từng số | Khớp (FIFO = LRU = 1000; OPT = 896, 844, ..., 428; 716, 574, 432, 290, 149) |
| Tính chất stack | LRU và OPT không tăng khi k tăng | Đúng ở mọi pattern |
| Uniform-Random | hit ratio FIFO/LRU so với k/20 | Lệch tối đa 0,3 điểm % (giới hạn 5) |
| Bảng T1, T2, T3 | Tính lại **từng ô** từ `summary.csv` và `belady.csv` | 0 ô sai (T1 chỉ lỗi mã hóa, xem mục 3) |
| `patterns.py` | Sequential/Loop/Belady đúng công thức; Locality: working set 5 trang không lặp mỗi pha, 92,4% tham chiếu nằm trong working set (kỳ vọng 92,5%); Skewed: 79,9% vào trang 0..3 (kỳ vọng 80%); Uniform: mỗi trang 4,6% đến 5,2%; cùng seed cho cùng chuỗi | Đạt đặc tả |
| Tái lập | Chạy lại toàn bộ thí nghiệm bằng code của Hiển | Cho ra **đúng nội dung** 3 file CSV Hiển đã nộp (Python 3.12.3) |

## 2. Những gì mình CHƯA kiểm tra được

1. **Các file ảnh PNG** của Hiển (chưa được gửi). Mình dựng lại biểu đồ bằng chính `make_charts.py` của Hiển trên CSV của Hiển và xem trực tiếp F4, F6 (giá trị đọc được như OPT của Sequential-20 là 74,0% = 740/1000 và Loop-8 là 29,0% = 290/1000 đều khớp CSV). Nếu muốn kiểm tra ảnh Hiển đã xuất, hãy gửi các file PNG.
2. **Phiên bản Python Hiển đã dùng.** Chuỗi ngẫu nhiên phụ thuộc phiên bản Python; bản chạy lại của mình dùng 3.12.3 và cho kết quả trùng, nên khả năng cao là cùng họ phiên bản. Hiển vẫn phải ghi phiên bản vào nhật ký chốt dữ liệu.
3. **Đối chiếu simulator online** (S5) vẫn là việc phải tự thao tác.
4. Kiểm tra này chứng minh số liệu **đúng so với engine và đặc tả**. Nó không thay thế việc nhóm hiểu và giải thích được vì sao ra kết quả đó.

## 3. Các điểm cần sửa (đã sửa trong 2 file kèm theo)

| # | Mức | Vấn đề | Cách sửa |
|---|---|---|---|
| 1 | **Cần sửa** | `T1_fault_rate_k4_k8.csv` và `.md` lưu ở mã hóa ISO-8859 (latin-1), không phải UTF-8. Dấu **±** hiển thị thành ký tự lỗi khi mở bằng trình soạn thảo/Word dùng UTF-8. Nguyên nhân: `open()` không chỉ định `encoding`, nên dùng mã mặc định của máy Hiển. | `make_charts.py`: ghi và đọc mọi file với `encoding="utf-8"`. Sau khi sửa, nội dung bảng không đổi, chỉ khác mã hóa. |
| 2 | **Nên sửa** | `--quick` và `--fake` ghi vào đúng `results/`. Chạy `--fake` (faults=0) sau khi chốt dữ liệu sẽ **ghi đè mất dữ liệu đã chốt**. | `--quick` và `--fake` giờ ghi vào `results_quick/`. Đã thử: `results/raw.csv` không đổi sau khi chạy hai chế độ này. |
| 3 | **Nên sửa** | Kiểu xuống dòng không ổn định. Module `csv` mặc định ghi CRLF, nhưng file Hiển gửi là LF, nên byte có thể khác nhau giữa các máy/lần chuyển file. Nội dung vẫn giống hệt. | `run_experiments.py` và `make_charts.py` luôn ghi LF (`lineterminator="\n"`). Bản sửa tái lập **đúng từng byte** 3 file CSV Hiển đã nộp. |
| 4 | **Nên sửa** | `run_experiments.py` chỉ tìm `engine.py` ở cùng thư mục, trong khi cấu trúc nhóm đặt engine ở `03_Son_Engine_Verification`. | Thêm tìm ở thư mục `../03_Son_Engine_Verification`. |
| 5 | Ghi nhận | `summary.csv` làm tròn mean/std/ratio về 4 chữ số. Không phải lỗi; sai số tối đa 5e-5, không ảnh hưởng bảng 1 chữ số thập phân. | Giữ nguyên. Các công cụ kiểm tra cho phép sai số này. |
| 6 | Ghi nhận | Tên file thật khác tài liệu cũ: hình tên `F1_Sequential-20.png`, `F6_grouped_k6.png`...; bảng nằm ở `tables/` (không phải `results/`); hình slide ở `figures/slide/` và tạo bằng `make_charts.py --slide`. | Đã cập nhật README các thư mục 01, 03, 04 cho khớp code. |
| 7 | Ghi nhận | `patterns.py` đạt đặc tả, **không cần sửa**. Cờ `--ref` trong `run_experiments.py` trỏ tới `engine_reference.py` không tồn tại; không ảnh hưởng vì không dùng. | Giữ nguyên. |

## 4. Cách áp dụng (Hiển thực hiện, Sơn kiểm tra)

1. Hiển thay `run_experiments.py` và `make_charts.py` trong `04_Hien_Experiments_Charts` bằng 2 file kèm theo (`patterns.py` giữ nguyên).
2. Hiển chạy lại: `python run_experiments.py`, rồi `python make_charts.py`, rồi `python make_charts.py --slide`. Ba file CSV phải **không đổi nội dung**; `T1` giờ là UTF-8.
3. Sơn chạy `python verification/audit_hien.py`: phải ra **32 đạt, 0 lỗi** và ghi `outputs/audit_hien.md`.
4. Sơn chạy `python verification/freeze_check.py` rồi dán nhật ký vào README gốc để chốt dữ liệu.

## 5. Lưu ý cho Đạt khi viết Discussion (từ `claim_evidence.py`)

- Với Locality-Phases và Skewed-80/20, LRU ít fault hơn FIFO ở **gần như mọi seed** (số seed LRU ít fault hơn FIFO, trên 30 seed: Skewed-80/20 đạt 30/30 ở **mọi** k; Locality-Phases đạt 30/30 ở k = 4, 5, 6, 7, 8, 10, còn k=3 là 28/30 và k=12 là 29/30). Với các ô đạt 30/30 có thể viết "LRU ít fault hơn FIFO trong cả 30 lần chạy", vì đây là so cặp trên cùng một chuỗi.
- Công cụ dùng quy tắc thận trọng của nhóm (chênh lệch trung bình so với std): các điểm Locality k=3, k=12 và Skewed k=3, k=4 chỉ ở mức **THẬN TRỌNG**; nên diễn đạt nhẹ ("có xu hướng"), trừ khi dẫn kèm số seed thắng/thua.
- Không được viết "LRU luôn tốt hơn FIFO": ở Uniform-Random hai thuật toán gần như ngang nhau, (LRU ít fault hơn FIFO chỉ khoảng 14 đến 19 trên 30 seed, tức gần như tung đồng xu), và trên chuỗi Belady với k=3, FIFO (9 fault) tốt hơn LRU (10 fault).
