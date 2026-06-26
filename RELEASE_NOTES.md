# Word Checker v1.0.0

Công cụ kiểm tra chính tả & định dạng file Word (.docx) trước khi nộp — chạy
offline, có cả dòng lệnh và giao diện web kéo-thả.

## Tính năng
- Kiểm tra **định dạng**: font, cỡ chữ, giãn dòng, canh lề, lề trang, thụt lề;
  cảnh báo khi dùng lẫn lộn nhiều font/cỡ chữ.
- Kiểm tra **lỗi văn bản**: cách đôi, dấu cách thừa/thiếu quanh dấu câu, đoạn
  trống thừa, lặp từ, viết hoa đầu câu, gạch nối `--`, lẫn lộn dấu nháy, chữ bỏ
  quên (Lorem ipsum, TODO...).
- Kiểm tra **chính tả tiếng Việt** theo từ điển (offline) và **AI/LLM** (tùy chọn).
- Kiểm tra **tiêu đề mục & đánh số** (nhảy cấp heading, số mục không liên tục).
- **Giới hạn số từ / số trang** (vd tiểu luận dưới 2000 từ).
- **Thống kê tài liệu**: số từ, số trang, thời gian đọc.
- **Tự động sửa** lỗi văn bản/chính tả và cả **định dạng** theo quy chuẩn.
- **Học quy chuẩn từ file mẫu** (`--template`).
- Xuất **comment trong Word**, báo cáo **HTML** và **PDF**, kết quả **JSON**.
- **Giảm nhiễu công thức toán** tự động cho tài liệu học thuật.

## Cách dùng nhanh (file .exe)
1. Tải `WordChecker.exe` ở mục Assets bên dưới.
2. Double-click để chạy — trình duyệt tự mở giao diện kéo-thả.
3. Kéo file `.docx` vào, chọn quy chuẩn, bấm Kiểm tra. Không cần cài Python.

> Lưu ý: chạy cục bộ trên máy bạn (localhost), file không gửi đi đâu.

## Dùng bằng mã nguồn
```bash
pip install -r requirements.txt
python webapp.py          # giao diện web
python cli.py bai.docx    # dòng lệnh
```
