# Word Checker v1.1.0

Công cụ kiểm tra chính tả & định dạng file Word trước khi nộp — chạy offline,
có cả dòng lệnh và giao diện web kéo-thả.

## Mới trong v1.1.0
- **Nhận file `.doc` cũ**: tự chuyển sang `.docx` để kiểm tra (cần máy có cài
  Microsoft Word hoặc LibreOffice). Dùng được cho cả CLI lẫn web app.
- **Soát cả bảng, đầu/chân trang và text box**: trước đây chỉ kiểm thân bài,
  nay bắt thêm lỗi cơ học & chính tả trong bảng biểu, header/footer, text box
  (gắn nhãn vị trí rõ ràng). Vẫn không kiểm định dạng ở những vùng này để tránh
  báo nhầm.
- **Từ điển chính tả mở rộng**: từ 65 lên 112 cặp lỗi thường gặp (hỏi/ngã, s/x,
  ch/tr, d/gi/r, lỗi gõ/bỏ dấu...), đã lọc kỹ để không báo nhầm từ đúng.

## Tính năng chính
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
3. Kéo file `.docx` (hoặc `.doc`) vào, chọn quy chuẩn, bấm Kiểm tra. Không cần
   cài Python.

> Lưu ý: chạy cục bộ trên máy bạn (localhost), file không gửi đi đâu.

## Dùng bằng mã nguồn
```bash
pip install -r requirements.txt
python webapp.py          # giao diện web
python cli.py bai.docx    # dòng lệnh
```
