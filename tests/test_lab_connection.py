
from pathlib import Path
from playwright.sync_api import Page, expect


def test_webwolf_connection(page: Page):
    # Dia chi WebWolf tren may cuc bo
    url = "http://127.0.0.1:19090/WebWolf/login"

    # Truy cap trang WebWolf
    response = page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    # Kiem tra phan hoi HTTP
    assert response is not None
    assert response.status == 200

    # Kiem tra nut dang nhap xuat hien
    login_button = page.get_by_role(
        "button",
        name="Sign In"
    )
    expect(login_button).to_be_visible()

    # Tao thu muc luu anh minh chung
    output = Path("06_Ket_qua_thuc_nghiem")
    output.mkdir(parents=True, exist_ok=True)

    # Chup anh giao dien WebWolf
    page.screenshot(
        path=str(output / "webwolf_playwright.png"),
        full_page=True
    )

    print("WebWolf connection: PASSED")
