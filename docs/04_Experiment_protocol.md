# Giao thức thực nghiệm tối thiểu 3 lần

## Chuẩn bị và nguồn dữ liệu
- WebGoat: `webgoat/webgoat:v2026.5`, kiểm tra digest thực tế từ `docker image inspect` và giấy phép gốc; ghi ngày tải, đường link https://owasp.org/www-project-webgoat/.
- Lab: 2 container `python:3.12-alpine`, hai phiên bản cùng nội dung, khác chính sách HTTPS.
- Chứng chỉ tự ký 30 ngày, SAN localhost/127.0.0.1, dùng riêng trên máy; không công khai key.
- Không có train/validation/test phân chia theo ML: dữ liệu là bộ kịch bản cấu hình tổng hợp có ground truth do nhóm gieo chủ động, không tự đánh giá khả năng suy rộng.

## Quy trình
1. Chạy `docker compose ps`, ghi lại cấu hình phần cứng và nguồn CPU/RAM.
2. Khóa công cụ qua `requirements-dt032.txt` và ghi manifest `python -m tools.record_manifest`.
3. Chạy `python -m tools.dt032_audit --repeat 3 --gate` không thay đổi cấu hình giữa các lượt.
4. Chạy `pytest ... --html ...` để có report có thể mở xem.
5. ZAP quét thụ động WebWolf/HTTPS Lab theo phạm vi localhost và lưu report.
6. Dùng `summary.json` lấy mean/std runtime, `results.csv` lập bảng phát hiện, không chọn chỉ run nhanh nhất.

## Thước đo
- Detection rate (recall) = TP / (TP + FN).
- Precision = TP / (TP + FP) khi có cảnh báo.
- False-positive rate = FP / (FP + TN).
- Coverage = số trường hợp được thực thi / 8 trường hợp ground truth; có thể báo cáo coverage test-suite mở rộng riêng.
- CI runtime: đo **thời gian end-to-end workflow trên GitHub Actions**, khác với `summary.json` runtime detector local.
- Stability: số lần đạt / tổng 3 lần; độ lệch chuẩn runtime.
- Cả detector và ground truth do nhóm định nghĩa → dễ bị thiên lệch, cần công bố hạn chế.

## Kết quả không được khẳng định nếu chưa chứng minh
- Không so metric trực tiếp với bài báo WebPKI vì khác đầu bài và dữ liệu.
- Không khẳng định Chrome chặn Mixed Content HTTP trên localhost; chỉ xác nhận scheme qua request.
- Không gắn nhãn TLS 1.2 yếu theo chuẩn chung; lab chỉ chấm khác biệt chính sách TLS-1.3-only.

## Dòng dữ liệu minh chứng
`run_01.json`, `run_02.json`, `run_03.json`, `results.csv`, `summary.json`, `environment_manifest.json`, pytest HTML/JSON, ZAP HTML và log OpenSSL.
