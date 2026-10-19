docker compose ps# GitHub Actions — CI Security Gate

**Mục đích:** Mỗi khi push hoặc tạo pull request, Github Actions thiết lập TLS local lab, chạy pytest, kiểm tra 4x2 phát hiện sai cấu hình, lặp 3 lần và tải report.

1. Trước khi commit: kiểm tra `.gitignore` chặn `certs/*.key`, `.venv`, `06_Ket_qua_thuc_nghiem`.
2. Tạo repository **private** để học tập nếu không cần công khai.
3. Mở VS Code Terminal trong project: `git init`, `git add .`, `git status`, chắc chắn không có khóa riêng, `git commit -m "DT032 baseline and hardened"`.
4. Đăng repo lên GitHub bằng GitHub Desktop/VS Code hoặc lệnh `git remote add origin ...` và `git push -u origin main` theo URL repository thực của bạn (không phát minh URL).
5. Tab **Actions → DT032 HTTPS Security Gate**, nhấn Run workflow hoặc push commit. Sau chạy, click job `local-https-security`.
6. Xem trạng thái `success` và tải `dt032-security-reports` trong mục Artifacts; ghi lại **end-to-end workflow runtime** (khác runtime detector).
7. Nếu có test fail hoặc `security gate: FAIL`, workflow đỏ là hành vi mong đợi; không bỏ qua bằng cách sửa expected ground truth.

**Lưu ý:** GitHub CI không chạy WebWolf vì tốn thêm WebGoat; chạy 17 tests (6 cũ trừ 1 WebWolf, thêm 12 mới). Bằng chứng WebWolf manual đã có ở Windows. CI tạo chứng chỉ *mới* mỗi lần, không commit khóa thật lên Git.

Workflow cung cấp bằng chứng CI, không chứng minh khả năng tương đương real-world websites.
