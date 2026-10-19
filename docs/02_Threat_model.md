# Threat Model / Tài sản, nguy cơ và ranh giới tin cậy

**Tài sản:** dữ liệu phiên và request trình duyệt, kết nối HTTPS, khóa riêng trong `certs/localhost.key`, kết quả quét, mã nguồn.

**Đối thủ giả định:** một tác nhân có khả năng gây thay đổi lưu lượng mạng khi người dùng truy cập HTTP, khai thác trang có script HTTP hoặc hưởng lợi từ cấu hình giao thức không phù hợp. Không mô phỏng đánh cắp khóa CA hay tấn công vào Internet.

**Luồng tin cậy:** Browser → HTTP 5080/5180 → HTTPS 5443/5543 → Python server trong Docker. ZAP chỉ làm proxy giữa trình duyệt và lab. WebGoat/WebWolf là mục tiêu giáo dục **khác** và không bị quét chủ động.

| Nguy cơ | Điểm kiểm tra | Dấu hiệu lỗi | Giảm thiểu |
|---|---|---|---|
| Người dùng vẫn ở HTTP | HTTP request | 200 thay vì 308 HTTPS | Redirect, cân nhắc HSTS preload ở môi trường thật |
| Không ghi nhớ chính sách HTTPS | HTTPS response | Thiếu/giá trị HSTS ngắn | Header HSTS hợp lệ trên HTTPS |
| Script tải qua HTTP | HTML + request browser | `script src=http://...` | HTTPS resource / relative source |
| Không đáp ứng chính sách TLS 1.3-only | TLS handshake | Server cho TLS 1.2 / không cho TLS 1.3 | Cấu hình cho TLS 1.3-only đối với lab |
| Host header đưa vào Location | GET với Host giả | Location chuyển qua domain người khác | Dùng hostname cố định/config allowlist |

**Giới hạn:** không đánh giá đầy đủ WebPKI, OCSP/CRL, CA chain hợp lệ ngoài lab, cipher suite review toàn diện, HSTS preload browser, mọi loại Mixed Content, MitM thực tế hay kỹ năng tấn công. TLS 1.2 có thể dùng an toàn trong production; không gọi TLS 1.2 là lỗ hổng tự thân.

**An toàn:** Cấu hình Docker chỉ publish 127.0.0.1; không chạy Active Scan trên domain không thuộc quyền sở hữu; không upload khóa riêng. Quy trình có thể ghi nhận không xác minh truy xuất nào ra ngoài.
