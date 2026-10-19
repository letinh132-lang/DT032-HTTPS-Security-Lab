
from pathlib import Path

import pytest
from playwright.sync_api import Browser


@pytest.mark.parametrize(
    "mode,port,expected_src",
    [
        (
            "vulnerable",
            5443,
            "http://localhost:5080/insecure.js",
        ),
        (
            "hardened",
            5543,
            "/secure.js",
        ),
    ],
)
def test_mixed_content(browser: Browser, mode, port, expected_src):
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    script_requests = []
    failed_requests = []

    page.on(
        "request",
        lambda req: script_requests.append(req.url)
        if req.resource_type == "script" else None,
    )

    page.on(
        "requestfailed",
        lambda req: failed_requests.append(req.url),
    )

    response = page.goto(
        f"https://localhost:{port}/",
        wait_until="load",
    )

    assert response is not None
    assert response.status == 200

    script_src = page.locator(
        "script[src]"
    ).get_attribute("src")

    assert script_src == expected_src

    if mode == "hardened":
        assert (
            "https://localhost:5543/secure.js"
            in script_requests
        )
        assert page.locator(
            "#resource-status"
        ).inner_text() == "JavaScript loaded"

    print(f"\nMode: {mode}")
    print(f"HTML script: {script_src}")
    print(f"Script requests: {script_requests}")
    print(f"Failed requests: {failed_requests}")

    output = Path("06_Ket_qua_thuc_nghiem")
    output.mkdir(parents=True, exist_ok=True)

    page.screenshot(
        path=str(output / f"mixed_{mode}.png"),
        full_page=True,
    )

    context.close()
