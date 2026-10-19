# Dàn ý báo cáo cuối 20–30 trang + slide

**Phần đầu:** bìa, lời cam đoan, tóm tắt, mục lục, danh mục hình/bảng, thuật ngữ (2–3 trang tùy quy định).

**Chương 1. Tổng quan và cơ sở lý thuyết (4–5 trang)**: HTTPS, TLS, HSTS, redirect, mixed content, WebPKI; bài báo DOI 10.1093/cybsec/tyaf018; so sánh bài báo và DT032; tối thiểu 5 khoảng trống do nhóm phân tích.

**Chương 2. Mô hình và phương pháp (5–6 trang)**: câu hỏi và giả thuyết, threat model, sơ đồ Docker/Playwright/ZAP/OpenSSL, bộ kiểm thử (12 test mở rộng + 6 cũ), ground truth và tiêu chí, manifest và lý do dùng chính sách TLS 1.3-only.

**Chương 3. Triển khai và thực nghiệm (7–9 trang)**: hai màn hình app, screenshot WebGoat/WebWolf, code trọng tâm, bảng Redirect/HSTS/Mixed Content/TLS, OpenSSL handshake, ba lần chạy, HTML/JSON/CSV, báo cáo ZAP, ảnh workflow CI, bảng mean/std runtime.

**Chương 4. Đánh giá và kết luận (4–5 trang)**: confusion matrix, test coverage, false positives/negatives, độ ổn định, phân tích giới hạn localhost/self-signed, công sức/chi phí thời gian & tài nguyên, đóng góp mới so với khung lý thuyết bài báo, hướng mở rộng.

**Tài liệu tham khảo + phụ lục**: bài báo Q1, RFC 6797 HSTS, OWASP TLS Cheat Sheet, OWASP ZAP docs, Playwright docs, tài liệu WebGoat, ảnh/URL nguồn. Sử dụng một kiểu trích dẫn thống nhất (IEEE/APA theo yêu cầu giảng viên).

**Slide 10–12 trang:** 1 tên đề tài; 2 vấn đề; 3 lý thuyết; 4 bài báo; 5 mục tiêu và tiêu chí; 6 kiến trúc; 7 baseline/hardened; 8 ma trận test; 9 kết quả OpenSSL; 10 ba lần chạy và metrics; 11 ZAP + CI; 12 kết luận/giới hạn.

**Bộ nộp:** mã nguồn sạch, README, giấy phép và checksum dữ liệu, bộ test, logs, results, report 20–30 trang, slides, video demo 3–5 phút (nếu thầy yêu cầu). Không nộp cert private key hay credentials.
