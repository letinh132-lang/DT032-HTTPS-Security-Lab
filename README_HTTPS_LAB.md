# DT032 — HTTPS Lab (Windows + Docker Desktop)

Lab được thiết kế để chạy cục bộ, chỉ ánh xạ cổng Docker lên `127.0.0.1` của máy Windows.

## Chuẩn bị

Trong thư mục gốc `C:\Users\Admin\DT032_HTTPS_Security` cần có:

- `docker-compose.yml`
- `05_Source_code\https_lab\server.py`
- `tests\test_https_lab_smoke.py` (kiểm tra cơ bản; không đè test WebWolf hiện có)
- `certs\localhost.crt` và `certs\localhost.key` mà bạn đã tạo ở bước trước.

KHÔNG đưa `certs/localhost.key` lên GitHub hoặc chia sẻ ra ngoài.

## Chạy

Mở PowerShell hoặc CMD trong thư mục gốc và chạy:

```powershell
docker compose up -d
docker compose ps
```

Đợi hai container ở trạng thái `Up` và xem log:

```powershell
docker compose logs --tail 20
```

Địa chỉ:

| Chế độ | HTTP | HTTPS |
|---|---|---|
| Vulnerable | http://localhost:5080 | https://localhost:5443 |
| Hardened | http://localhost:5180 | https://localhost:5543 |

Vì chứng chỉ là self-signed, trình duyệt có thể cảnh báo không tin cậy. Chỉ sử dụng địa chỉ localhost do bạn sở hữu. Để xác minh HTTP/TLS mà không bỏ qua xác thực chứng chỉ, sử dụng `curl.exe --cacert certs\localhost.crt` trên máy hỗ trợ option này.

## Kiểm tra từ PowerShell / CMD

```powershell
curl.exe -i http://localhost:5080/
curl.exe -i http://localhost:5180/
curl.exe --cacert certs\localhost.crt -i https://localhost:5443/
curl.exe --cacert certs\localhost.crt -i https://localhost:5543/
```

- Vulnerable HTTP: mã 200 (không redirect).
- Hardened HTTP: mã 308 cùng `Location: https://localhost:5543/`.
- Vulnerable HTTPS: không có header HSTS, có `http://localhost:5080/insecure.js`.
- Hardened HTTPS: có `Strict-Transport-Security: max-age=31536000`, đường dẫn script `/secure.js`.

Kiểm thử nhanh bằng Python đã cài trong `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_https_lab_smoke.py -v
```

Khi kiểm chứng TLS, hãy phân biệt: TLS 1.2 có thể vẫn an toàn trong thực tế; đề tài này dùng chính sách nội bộ *chỉ TLS 1.3* làm tiêu chí kiểm tra nghiêm ngặt.

**Mixed content:** Trên loopback (`localhost`) trình duyệt có thể có ngoại lệ dành cho nguồn được xem là đáng tin cậy. Vì vậy bài lab kiểm tra tham chiếu `http://...` trong HTML, không khẳng định mọi trình duyệt sẽ chặn script HTTP trong lab. Trong thực nghiệm sau, cần ghi rõ cách phát hiện, điều kiện và giới hạn này.

**HSTS:** Đánh giá hiện diện và giá trị header trên HTTPS. HSTS liên quan đến hành vi trình duyệt và không thể được kết luận chỉ từ việc có header, nhất là với chứng chỉ tự ký và việc dùng localhost/IP.

## Dừng lab

```powershell
docker compose down
```

Lệnh này chỉ dừng và gỡ hai container thuộc dự án compose này, không xóa WebGoat/WebWolf.
