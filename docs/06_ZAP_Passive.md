# Đối chiếu ZAP — CHỈ THỰC NGHIỆM LOCAL

1. Chạy Docker lab (5080, 5180, 5443, 5543), WebGoat/WebWolf nếu cần.
2. Mở ZAP 2.17.0. `Tools → Options → Network → Local Servers/Proxies`, main proxy `127.0.0.1:18081` (theo máy người dùng).
3. `Quick Start → Manual Explore`. Mở **mỗi lab một lần**, bắt đầu với `http://127.0.0.1:5080/`, sau đó `https://localhost:5443/`; lặp với `http://127.0.0.1:5180/` và `https://localhost:5543/`.
3b. Dùng `http://127.0.0.1:18080/WebGoat` và `http://127.0.0.1:19090/WebWolf/login` làm bằng chứng **OWASP WebGoat/WebWolf** thuộc mục dữ liệu đề bài. Không đưa WebGoat vào 8 ground-truth cases vì không kiểm soát chính xác 4 sai cấu hình của nó.
4. Trình duyệt phải là cửa sổ do ZAP tạo; không cấu hình proxy toàn bộ trình duyệt cá nhân. Nếu browser từ chối self-signed cert, chỉ ngoại lệ trong trình duyệt của lab; không tắt kiểm tra chứng chỉ của toàn hệ thống.
5. Trong Sites/History, chọn URL tương ứng, mở Request, Response. Đợi Passive Scan kết thúc và xem Alerts. **Không bấm Active Scan/Attack**.
6. Kết quả có thể có HSTS missing hoặc Secure Pages Include Mixed Content cho Vulnerable; ZAP có thể phát hiện thêm lỗi header khác. Không khẳng định sẽ luôn phát hiện TLS version hay HSTS của self-signed localhost.
7. `Report → Generate Report` (giao diện menu tùy bản), xuất HTML/JSON vào `06_Ket_qua_thuc_nghiem/`, gợi ý `zap_vulnerable.html`, `zap_hardened.html`.
8. Lập bảng đối chiếu từng finding 4 mục: detected by Python, detected by ZAP, giải thích nếu ZAP không có rule/cảnh báo nhầm. Ghi ZAP version và add-ons.

**Quan trọng:** ZAP đang ở trên Windows, không cần chạy ZAP bằng Docker. Chỉ sử dụng site thuộc quyền sở hữu hoặc được cấp phép. Không phải mọi cảnh báo trong ZAP là lỗ hổng đã xác nhận.

Tài liệu chính thức: https://www.zaproxy.org/docs/docker/baseline-scan/ (baseline scanning là thụ động); https://www.zaproxy.org/docs/desktop/start/features/pscan/.
