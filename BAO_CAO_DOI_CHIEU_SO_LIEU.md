# Báo cáo đối chiếu số liệu

Đối tượng kiểm tra: `patterns.py`, `run\_experiments.py`, `make\_charts.py`, `raw.csv`, `summary.csv`, `belady.csv`, `T1`, `T2`, `T3` (cả `.csv` và `.md`) do Hiển gửi.

## 1\. Kết luận

**Số liệu của Hiển chính xác.** Không có số nào sai. Có 4 điểm cần sửa trong code và định dạng file (mục 3); các điểm này **không làm đổi con số nào**.

|Hạng mục|Cách kiểm tra|Kết quả|
|-|-|-|
|`raw.csv`, 2208 dòng|Sinh lại từng chuỗi bằng `patterns.py` + đúng seed, rồi tính bằng **hai bộ mô phỏng**: `engine.py` của Sơn và một bộ **độc lập viết kiểu khác** (danh sách thuần, không dùng `OrderedDict`/`deque`)|**2208/2208 dòng trùng** faults, hits, compulsory ở cả hai bộ|
|Lưới thí nghiệm|So với tập (pattern, thuật toán, k, seed) kỳ vọng|Không thiếu, không thừa, không trùng dòng nào|
|Ràng buộc từng dòng|N=1000; hits+faults=N; compulsory ≤ faults ≤ N; fault\_rate = faults/N|Đạt cả 2208 dòng|
|OPT ≤ FIFO và OPT ≤ LRU|Mọi cặp (pattern, k, seed)|Không vi phạm|
|`summary.csv`, 120 dòng|Tính lại mean, std mẫu (n-1), rate, ratio\_to\_OPT, runs từ `raw.csv`|Đúng; sai lệch chỉ do làm tròn (lớn nhất: mean 3,3e-5; std 4,8e-5; ratio 4,9e-5)|
|`belady.csv`, 18 dòng|Hai bộ mô phỏng + giá trị vàng G2|Đúng; FIFO k=3 → 9, k=4 → 10|
|Giá trị vàng G3 (Sequential-20), G4 (Loop-8)|So từng số|Khớp (FIFO = LRU = 1000; OPT = 896, 844, ..., 428; 716, 574, 432, 290, 149)|
|Tính chất stack|LRU và OPT không tăng khi k tăng|Đúng ở mọi pattern|
|Uniform-Random|hit ratio FIFO/LRU so với k/20|Lệch tối đa 0,3 điểm % (giới hạn 5)|
|Bảng T1, T2, T3|Tính lại **từng ô** từ `summary.csv` và `belady.csv`|0 ô sai (T1 chỉ lỗi mã hóa, xem mục 3)|
|`patterns.py`|Sequential/Loop/Belady đúng công thức; Locality: working set 5 trang không lặp mỗi pha, 92,4% tham chiếu nằm trong working set (kỳ vọng 92,5%); Skewed: 79,9% vào trang 0..3 (kỳ vọng 80%); Uniform: mỗi trang 4,6% đến 5,2%; cùng seed cho cùng chuỗi|Đạt đặc tả|
|Tái lập|Chạy lại toàn bộ thí nghiệm bằng code của Hiển|Cho ra **đúng nội dung** 3 file CSV Hiển đã nộp (Python 3.12.3)|

## 2\. Các điểm cần sửa (đã sửa trong 2 file kèm theo)

|#|Mức|Vấn đề|Cách sửa|
|-|-|-|-|
|1|**Cần sửa**|`T1\_fault\_rate\_k4\_k8.csv` và `.md` lưu ở mã hóa ISO-8859 (latin-1), không phải UTF-8. Dấu **±** hiển thị thành ký tự lỗi khi mở bằng trình soạn thảo/Word dùng UTF-8. Nguyên nhân: `open()` không chỉ định `encoding`, nên dùng mã mặc định của máy Hiển.|`make\_charts.py`: ghi và đọc mọi file với `encoding="utf-8"`. Sau khi sửa, nội dung bảng không đổi, chỉ khác mã hóa.|
|2|**Nên sửa**|`--quick` và `--fake` ghi vào đúng `results/`. Chạy `--fake` (faults=0) sau khi chốt dữ liệu sẽ **ghi đè mất dữ liệu đã chốt**.|`--quick` và `--fake` giờ ghi vào `results\_quick/`. Đã thử: `results/raw.csv` không đổi sau khi chạy hai chế độ này.|
|3|**Nên sửa**|Kiểu xuống dòng không ổn định. Module `csv` mặc định ghi CRLF, nhưng file Hiển gửi là LF, nên byte có thể khác nhau giữa các máy/lần chuyển file. Nội dung vẫn giống hệt.|`run\_experiments.py` và `make\_charts.py` luôn ghi LF (`lineterminator="\\n"`). Bản sửa tái lập **đúng từng byte** 3 file CSV Hiển đã nộp.|
|4|**Nên sửa**|`run\_experiments.py` chỉ tìm `engine.py` ở cùng thư mục, trong khi cấu trúc nhóm đặt engine ở `03\_Son\_Engine\_Verification`.|Thêm tìm ở thư mục `../03\_Son\_Engine\_Verification`.|
|5|Ghi nhận|`summary.csv` làm tròn mean/std/ratio về 4 chữ số. Không phải lỗi; sai số tối đa 5e-5, không ảnh hưởng bảng 1 chữ số thập phân.|Giữ nguyên. Các công cụ kiểm tra cho phép sai số này.|
|6|Ghi nhận|Tên file thật khác tài liệu cũ: hình tên `F1\_Sequential-20.png`, `F6\_grouped\_k6.png`...; bảng nằm ở `tables/` (không phải `results/`); hình slide ở `figures/slide/` và tạo bằng `make\_charts.py --slide`.|Đã cập nhật README các thư mục 01, 03, 04 cho khớp code.|
|7|Ghi nhận|`patterns.py` đạt đặc tả, **không cần sửa**. Cờ `--ref` trong `run\_experiments.py` trỏ tới `engine\_reference.py` không tồn tại; không ảnh hưởng vì không dùng.|Giữ nguyên.|

## 3\. RE-TAKE

1. Hiển thay `run\_experiments.py` và `make\_charts.py` trong `04\_Hien\_Experiments\_Charts` bằng 2 file kèm theo (`patterns.py` giữ nguyên).
2. Hiển chạy lại: `python run\_experiments.py`, rồi `python make\_charts.py`, rồi `python make\_charts.py --slide`. Ba file CSV phải **không đổi nội dung**; `T1` giờ là UTF-8.
3. Sơn chạy `python verification/audit\_hien.py`: phải ra **32 đạt, 0 lỗi** và ghi `outputs/audit\_hien.md`.
4. Sơn chạy `python verification/freeze\_check.py` rồi dán nhật ký vào README gốc để chốt dữ liệu.

## 

