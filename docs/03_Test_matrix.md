# Ma trận kiểm thử và ground truth

| ID | Đối tượng | Kiểu test | Kỳ vọng | Bằng chứng |
|---|---|---|---|---|
| R-NEG | Vulnerable HTTP 5080 | Negative | Trả 200; detector gắn nhãn redirect missing | header, JSON |
| R-POS | Hardened HTTP 5180 | Positive | Trả 308; Location trỏ 5543, giữ query | header, JSON |
| H-NEG | Vulnerable HTTPS 5443 | Negative | Không có HSTS | header, JSON |
| H-POS | Hardened HTTPS 5543 | Positive | HSTS max-age >= 31536000 | header, JSON |
| M-NEG | Vulnerable HTTPS 5443 | Negative | `script[src]` dùng HTTP; detector phát hiện | HTML, URL request |
| M-POS | Hardened HTTPS 5543 | Positive | Script là đường dẫn tương đối, request HTTPS | HTML, URL request |
| T-NEG | Vulnerable TLS | Negative *theo policy* | TLS 1.2 được chấp nhận; TLS 1.3 bị từ chối | OpenSSL, JSON |
| T-POS | Hardened TLS | Positive | TLS 1.2 từ chối; TLS 1.3 chấp nhận | OpenSSL, JSON |
| E-HSTS | Hardened HTTP | Edge | Header HSTS không được đặt trên HTTP | pytest |
| E-HOST | Hardened HTTP | Edge | Header Host giả không ảnh hưởng Location | pytest |
| E-404-B | Vulnerable | Edge | Unknown HTTP path trả 404 | pytest |
| E-404-H | Hardened | Edge | Unknown HTTP path redirect (HTTPS mới trả 404) | pytest |

**Phân biệt:** 4 x 2 = 8 quan sát ở công cụ phát hiện, 12 test mới trong pytest. Chỉ 8 quan sát gốc có ground truth dương/âm và được tính confusion matrix.

**Không nhầm lẫn:** `pytest PASSED` cho R-NEG/H-NEG... nghĩa là **hệ thống phát hiện được cấu hình sai đã gieo**, không phải điểm an toàn cao cho Vulnerable.
