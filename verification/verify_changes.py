from playwright.sync_api import sync_playwright, expect

def verify_changes(page):
    # Hook up console
    page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

    # 1. Load the page
    page.goto("http://localhost:8080/index.html")

    # 2. Wait for GUI.board to be ready
    print("Waiting for GUI.board...")
    page.wait_for_function("window.GUI && window.GUI.board")

    # Also wait for pieces to be visible to ensure board is rendered
    page.wait_for_selector(".piece-417db")
    print("Board initialized.")

    # 3. Import a game via PGN
    print("Importing PGN...")
    pgn = "1. e4 e5 2. Nf3 Nc6"
    page.evaluate(f"""
        document.getElementById('pgnText').value = "{pgn}";
        importManualPGN();
    """)

    # Wait a bit for load to finish
    page.wait_for_timeout(1000)

    # 4. Click "Pro Analysis" tab (it might already be active)
    page.click("#tab-analysis")

    # 5. Click "Full Analysis"
    print("Clicking Full Analysis...")
    page.click("#scanBtn")

    # 6. Expect the toast error about API key
    # Increase timeout to 30s just in case engine interactions cause delays
    print("Waiting for toast...")
    toast = page.locator(".custom-toast.error")
    expect(toast).to_contain_text("Please set API Key in Settings!", timeout=30000)

    print("Toast appeared as expected. Verification successful.")

    # 7. Take screenshot
    page.screenshot(path="verification/verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_changes(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
            # Dump logs
            try:
                logs = page.evaluate("window.sys_logs")
                print("System Logs:", logs)
            except:
                pass
        finally:
            browser.close()
