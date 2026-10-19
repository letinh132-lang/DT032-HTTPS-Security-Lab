"""Render an offline report from measured DT032 audit results (no external assets)."""
import html
import json
from pathlib import Path
from tools.dt032_audit import OUTPUT, CHECKS


def main():
    source = OUTPUT / 'summary.json'
    if not source.exists():
        raise SystemExit('Run: python -m tools.dt032_audit --repeat 3 --gate first')
    data = json.loads(source.read_text(encoding='utf-8'))
    runs = data['all_runs']
    bars = '\n'.join(f'<div class="bar"><b>Lần {row["iteration"]}</b><span style="width:{max(5, row["duration_sec"] / max(x["duration_sec"] for x in runs) * 100):.1f}%">{row["duration_sec"]:.3f}s</span></div>' for row in runs)
    rows = '\n'.join(
        '<tr>' + ''.join(f'<td>{html.escape(str(value))}</td>' for value in (
            r['iteration'], r['duration_sec'], r['metrics']['TP'], r['metrics']['FN'],
            r['metrics']['FP'], r['metrics']['TN'],
            r['metrics']['detection_rate'], r['metrics']['false_positive_rate'],
        )) + '</tr>' for r in runs
    )
    body = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>DT032 — Báo cáo thực nghiệm 3 lần</title>
<style>body{{font:16px system-ui,Arial,sans-serif;max-width:1040px;margin:36px auto;padding:0 22px;color:#1f2937}}h1{{color:#0f3557}}h2{{border-bottom:1px solid #dbe3ea;padding-bottom:9px}}p{{line-height:1.7}}.metrics{{display:flex;gap:16px;flex-wrap:wrap}}.stat{{border:1px solid #dbe3ea;border-radius:10px;padding:18px;flex:1;min-width:170px}}.stat strong{{font-size:29px;display:block}}.stat small{{color:#64748b}}table{{border-collapse:collapse;width:100%;margin-top:16px}}th,td{{text-align:left;border:1px solid #dbe3ea;padding:11px}}th{{background:#f2f6fa}}.bar{{display:flex;gap:18px;align-items:center;margin:16px 0}}.bar b{{width:62px}}.bar span{{display:block;background:#294d71;color:white;border-radius:4px;padding:10px;box-sizing:border-box;min-width:65px}}.note{{border-left:4px solid #b45309;padding:11px 14px;background:#fffbeb}}code{{background:#eef2f6;padding:2px 4px}}</style></head><body>
<h1>DT032 — Kết quả thực nghiệm kiểm thử HTTPS</h1>
<p>Dữ liệu thực nghiệm được đọc trực tiếp từ <code>security_audit/summary.json</code>; không dùng số liệu giả. Số lần chạy: <b>{data['repetitions']}</b>.</p>
<div class="metrics"><div class="stat"><small>Trung bình runtime</small><strong>{data['mean_runtime_sec']:.4f}s</strong></div><div class="stat"><small>Độ lệch chuẩn</small><strong>{data['std_runtime_sec']:.4f}s</strong></div><div class="stat"><small>Ground truth / lượt</small><strong>4+4</strong><small>4 vi phạm gieo; 4 cấu hình đạt</small></div></div>
<h2>Thời gian từng lần chạy</h2>{bars}
<h2>Bảng phát hiện cấu hình</h2><table><thead><tr><th>Lần</th><th>Thời gian (s)</th><th>TP</th><th>FN</th><th>FP</th><th>TN</th><th>Recall</th><th>FPR</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Định nghĩa và giới hạn</h2><p>Recall = TP/(TP+FN). FPR = FP/(FP+TN). Trường hợp đánh giá gồm {len(CHECKS)} loại chính sách × 2 chế độ, dựa trên sai cấu hình do nhóm chủ động gieo vào lab.</p>
<p class="note"><b>Không suy rộng:</b> Test được thiết kế dựa trên chính cùng lab và chính sách của nhóm. TLS 1.2 không tự thân là yếu; dự án đặt mục tiêu TLS 1.3-only. Dùng localhost nên không thể dùng kết quả này làm bằng chứng trình duyệt luôn chặn Mixed Content hay HSTS hoạt động đầy đủ với chứng chỉ tự ký. Thời gian detector không phải thời gian CI end-to-end.</p>
</body></html>'''
    dest = OUTPUT / 'experiment_report.html'
    dest.write_text(body, encoding='utf-8')
    print('Created', dest)


if __name__ == '__main__':
    main()
