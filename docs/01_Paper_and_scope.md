# Nguồn gốc đề tài và bản đồ đối chiếu bài báo

**Đề tài chính:** DT032 — Phòng thủ hạ cấp giao thức và cấu hình sai HTTPS trong ứng dụng mẫu.

**Bài báo:** Karl Grindal, Milton Mueller, Vagisha Srivastava (2025), "Non-governmental governance of trust on the internet: WebPKI as public good", *Journal of Cybersecurity* 11(1), tyaf018. DOI https://doi.org/10.1093/cybsec/tyaf018

**Phân biệt quan trọng:** Bài báo phân tích thể chế, phối hợp của CAs và trình duyệt trong WebPKI; **không** công bố bộ mã nguồn kiểm thử Redirect/HSTS/Mixed Content/TLS. DT032 là tái lập có chọn lọc về **khung khái niệm xác thực và niềm tin**, sau đó thực hiện **một mở rộng kỹ thuật độc lập** trên ứng dụng lab.

| Thành phần nghiên cứu | Nội dung bài báo / vai trò | DT032 kế thừa và mở rộng |
|---|---|---|
| Vấn đề | Cơ chế tạo niềm tin vào danh tính website và chứng chỉ | Giải thích vì sao kiểm tra chứng chỉ/TLS và cấu hình website là quan trọng |
| Phương pháp | Phân tích thể chế và các bên tham gia WebPKI | Không tái lập định lượng; chuyển hóa thành mô hình kiểm thử kỹ thuật trong lab |
| Dữ liệu bài báo | Thông tin CA/B Forum, chính sách/chứng chỉ và tương tác giữa các chủ thể | **Khác dữ liệu**: WebGoat & app tổng hợp local; phải thừa nhận không cùng dataset |
| Thước đo bài báo | Khả năng duy trì niềm tin, mức hiệu quả các cơ chế quản trị | Metric tự đề xuất: coverage, TP/FN/FP/TN, runtime, tính ổn định |
| Kết quả mong đợi DT032 | Cấu hình có sai sót được phát hiện và hardened vượt qua chính sách | Không so số liệu thô với số liệu bài báo do khác đối tượng |

**Ít nhất 5 hạn chế/khoảng trống khi áp dụng bài báo vào DT032 (là phân tích của nhóm):**
1. Đối tượng phân tích là quản trị WebPKI, không phải bộ phát hiện cấu hình HTTPS tự động.
2. Không công bố ground truth gồm bốn lỗi DT032 và phiên bản ứng dụng cố ý cấu hình sai.
3. Không có unit/negative test suite để tái chạy trực tiếp.
4. Các thước đo thể chế không đo CI runtime hay tỷ lệ phát hiện lỗi kỹ thuật.
5. Kết luận trên hệ sinh thái toàn cầu không trực tiếp suy rộng từ môi trường localhost tự ký và một container.

**Câu hỏi nghiên cứu:** RQ1: Test suite có phát hiện đúng các sai cấu hình được gieo trong lab? RQ2: Hardened loại bỏ được các sai cấu hình này theo chính sách nào? RQ3: Mức ổn định và runtime qua 3 lần chạy? RQ4: ZAP đối chiếu được bao nhiêu phát hiện, có cảnh báo sai/không tương đương?

**Không tuyên bố** tái lập nguyên số liệu/tái huấn luyện mô hình hoặc vượt bài báo gốc. Trích dẫn cụ thể theo trang/đề mục sau khi đọc toàn văn.
