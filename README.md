# Dự án OSG: Mô phỏng bộ nhớ ảo và thay trang (Virtual Memory & Page Replacement Simulator)

**Chủ đề nghiên cứu:** Ảnh hưởng của kiểu truy cập (Effect of access patterns)
**Môn học:** OSG (Operating System)
**Thuật toán so sánh:** FIFO, LRU, OPT (Optimal)

## 1. Dự án này làm gì?
Nhóm viết một chương trình mô phỏng việc hệ điều hành thay trang trong RAM. Ta cho chương trình chạy
cùng một thuật toán (FIFO, LRU, OPT) với nhiều "kiểu truy cập" khác nhau (tuần tự, vòng lặp, ngẫu nhiên...)
rồi đếm số lần **page fault** (truy cập trang chưa có trong RAM). Kết quả cho biết kiểu truy cập ảnh hưởng
thế nào đến hiệu năng của từng thuật toán. Từ đó nhóm viết báo cáo và làm slide thuyết trình.

                  
  01_Dat_Report_Slides/              Tô Thanh Đạt: viết Báo cáo và làm Slide
  02_Khanh_Core_Knowledge/           Phạm Nam Khánh: kiến thức lõi, đối chiếu Slide với Giáo trình
  03_Son_Engine_Verification/        Huỳnh Tiến Sơn: engine mô phỏng, kiểm thử, kiểm tra số liệu
  04_Hien_Experiments_Charts/        Nguyễn Hưng Hiển: sinh dữ liệu, chạy thí nghiệm, vẽ biểu đồ
```

## 3. Ai giao gì cho ai
| Người giao | Người nhận | Nội dung | Hạn |
|---|---|---|---|
| Sơn (03) | Hiển (04) | file `engine.py` (Hiển cần nó để chạy thí nghiệm) | Ngày 1, 21:00 |
| Khánh (02) | Đạt (01) | bảng đối chiếu Slide với Giáo trình | Ngày 2, 10:00 |
| Hiển (04) | Đạt (01) | file CSV, biểu đồ, bảng T1-T3 | Ngày 2, 15:00 |
| Sơn (03) | Đạt (01) | bảng trace ví dụ G1 và Belady | Ngày 2, 15:00 |
| Hiển (04) | Sơn (03) | file CSV để Sơn kiểm tra | Ngày 2, 12:00 (chốt dữ liệu) |
| Sơn (03) | Đạt (01) | danh sách số trong Báo cáo đã đối chiếu với CSV | Ngày 3 |

## 4. Thứ tự chạy (mỗi lệnh chạy BÊN TRONG thư mục của chủ sở hữu)
1. Sơn: vào `03_Son_Engine_Verification`, chạy `python -m unittest discover -s tests` (phải ra chữ **OK**).
2. Hiển: vào `04_Hien_Experiments_Charts`, chạy `python -m unittest discover -s tests`, rồi `python run_experiments.py`.
3. Sơn: vào `03_Son_Engine_Verification`, chạy `python verification/verify_results.py` để kiểm tra dữ liệu của Hiển.
4. Hiển: chạy `python make_charts.py` để vẽ biểu đồ.

## 5. Yêu cầu cài đặt
- Python 3.10 trở lên (kiểm tra bằng `python --version`, ghi lại phiên bản khi chốt dữ liệu).
- Thư viện `matplotlib` chỉ cần để vẽ biểu đồ (`pip install matplotlib`).

## 6. Quy tắc quan trọng
- Mọi tham số thí nghiệm đã **cố định** trong tài liệu đặc tả. **Không chỉnh tham số để kết quả "đẹp".**
- Mỗi người chỉ sửa file trong thư mục của mình.
- Không tự sửa số liệu. Nếu số trong Báo cáo khác file CSV, báo cho Sơn.

