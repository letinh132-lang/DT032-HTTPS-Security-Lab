# DT032 — Bộ bổ sung cho project đã chạy 6/6 pytest

Bộ này chỉ **bổ sung** file mới. Không xóa hay thay thế `docker-compose.yml`, `server.py`, 3 bài test cũ hoặc chứng chỉ `certs/`.

## 1. Chép vào đúng thư mục

Giải nén; chép **nội dung bên trong** vào `C:\Users\Admin\DT032_HTTPS_Security\`.
Mở terminal VS Code tại thư mục gốc và chạy `docker compose ps` (hai app phải `Up`).

## 2. Bước 3.3 — Ground truth và 12 positive/negative tests mới

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security_policy_matrix.py -v
```

Có 8 bài kiểm tra cặp 4 lỗi x 2 ứng dụng, 1 test HSTS không xuất hiện trên HTTP, 1 test chống Host header injection khi redirect, và 2 test đường dẫn không tồn tại = **12 tests**.
Trong chế độ vulnerable, `PASSED` nghĩa là *đã phát hiện đúng lỗi cài đặt có chủ đích*, không phải trang web an toàn.

Chạy lại toàn bộ để có **18 trường hợp** (6 cũ + 12 mới):

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v --html="06_Ket_qua_thuc_nghiem\pytest_report_extended.html" --self-contained-html --json-report --json-report-file="06_Ket_qua_thuc_nghiem\pytest_results_extended.json"
```

## 3. Bước 3.4–3.5 — Chạy 3 lần, tính detection rate và runtime

```powershell
.\.venv\Scripts\python.exe -m tools.dt032_audit --repeat 3 --gate
```

Đầu ra tự tạo:
- `06_Ket_qua_thuc_nghiem/security_audit/run_01.json`, `run_02.json`, `run_03.json` — bằng chứng từng lần.
- `.../security_audit/results.csv` — 24 dòng (8 ca đánh giá mỗi lần x 3 lần).
- `.../security_audit/summary.json` — trung bình và độ lệch chuẩn runtime.

Quy ước **ground truth**: với 4 điều kiện mà chính project đã cài cố ý, baseline có 4 vi phạm và hardened có 0. Mỗi lượt có 8 quan sát (4 tiêu chí x 2 hệ thống). Khi all-correct sẽ có TP=4, TN=4, FP=0, FN=0, detection rate=100% **chỉ trên bộ kiểm thử nhỏ này**. Không khẳng định độ chính xác trên website thực tế.

Tạo báo cáo thực nghiệm dễ xem trên Chrome:

```powershell
.\.venv\Scripts\python.exe -m tools.make_experiment_report
```

Mở `06_Ket_qua_thuc_nghiem/security_audit/experiment_report.html`.

Định nghĩa: detection rate = TP/(TP+FN); false-positive rate = FP/(FP+TN); test coverage = số trường hợp đã chạy / số trường hợp thiết kế; runtime=thời gian lần chạy.

**Thận trọng:** TLS 1.2 không mặc nhiên là yếu; đây là vi phạm tiêu chuẩn chính sách TLS 1.3-only của lab. `localhost` là nguồn đặc biệt nên Playwright có thể thực thi script HTTP; metric ở đây phát hiện `script[src]` HTTP trên trang HTTPS, không đo hiệu quả browser blocking. HSTS với self-signed certificate và localhost cũng chỉ được đo ở mức header cấu hình.

## 4. Bước 3.5 — Lưu manifest để tái lập

```powershell
.\.venv\Scripts\python.exe -m tools.record_manifest
.\.venv\Scripts\python.exe -m pip freeze > requirements-local-freeze.txt
```

Lưu `requirements-local-freeze.txt`, `environment_manifest.json` cùng mã nguồn. File `.gitignore` ngăn upload `certs/*.key`, `certs/*.crt`, báo cáo và `.venv/`.

## 5. Bước 3.6 — ZAP và CI security gate

- Đọc `docs/06_ZAP_Passive.md`, quét thụ động localhost, xuất báo cáo HTML và JSON từ menu ZAP.
- Đọc `docs/07_CI_Guide.md`, đưa **source code không kèm khóa riêng** lên GitHub để chạy `.github/workflows/dt032-security.yml`.
- CI tạo chứng chỉ tạm, chạy Docker lab, 17 test độc lập WebWolf, chạy detector 3 lần, fail nếu baseline faults bị bỏ sót hoặc hardened có sai cấu hình.
- Test WebWolf chạy thủ công ở máy cá nhân vì CI không triển khai WebGoat mặc định.

## 6. Hoàn thiện học thuật và báo cáo

Xem thêm tài liệu:
- `docs/01_Paper_and_scope.md`
- `docs/02_Threat_model.md`
- `docs/03_Test_matrix.md`
- `docs/04_Experiment_protocol.md`
- `docs/05_Report_outline.md`
- `docs/06_ZAP_Passive.md`
- `docs/07_CI_Guide.md`

## Lỗi thường gặp

- `ModuleNotFoundError: No module named tools`: đứng sai thư mục, hãy `cd C:\Users\Admin\DT032_HTTPS_Security`.
- `Connection refused`: chạy `docker compose up -d`; kiểm tra các cổng 5080/5180/5443/5543.
- `certificate verify failed`: file cert có thể đã bị thay thế mà hai container chưa tải lại; `docker compose down` rồi `docker compose up -d`.
- `Port occupied`: xem `docker ps`, không thay đổi ports tùy ý nếu chưa cập nhật scanner.
- `WebGoat unhealthy`: không ảnh hưởng test HTTPS lab; để ý nếu chạy riêng bài test WebWolf.
