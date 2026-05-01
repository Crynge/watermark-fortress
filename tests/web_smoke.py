import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    base_url = os.getenv("FORTRESS_WEB_URL", "http://127.0.0.1:5174/?apiBase=http://127.0.0.1:8011")
    output_dir = Path("tests/artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1300})
        page.goto(base_url, wait_until="networkidle")
        page.get_by_text("Mission brief", exact=True).wait_for()
        page.screenshot(path=str(output_dir / "fortress-overview.png"), full_page=True)
        page.locator('textarea[placeholder="Paste text to watermark and stress-test..."]').fill(
            "Because market integrity is important, however, provenance must remain resilient after aggressive rewrites."
        )
        page.get_by_role("button", name="mixed_pressure").click()
        page.get_by_text("Run Fortress Battle", exact=True).click()
        page.wait_for_timeout(1400)
        page.get_by_text("Verdict ladder", exact=True).wait_for()
        page.screenshot(path=str(output_dir / "fortress-battle.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
