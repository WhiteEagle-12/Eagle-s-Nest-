
from playwright.sync_api import sync_playwright

def verify_logic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Load the page
        print("Loading page...")
        page.goto("http://localhost:8000/index.html")

        # 2. Wait for Scanner to be available
        print("Waiting for Scanner...")
        # We can't easily wait for a JS variable to exist directly with a locator,
        # but we can poll for it.
        page.wait_for_function("() => typeof window.Scanner !== 'undefined'")

        # 3. Test getDetailedMoveStats
        print("Testing Scanner.getDetailedMoveStats...")
        result = page.evaluate("""
            () => {
                const chess = new Chess();
                // rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
                // White material: 8*1 + 2*3 + 2*3 + 2*5 + 9 = 39
                // Black material: 39
                // Net for White ('w'): 0
                // Center control: 0 (no pieces on d4, d5, e4, e5)

                const statsStart = Scanner.getDetailedMoveStats(chess, 'w');

                chess.move('e4');
                // Center: Pawn on e4 (one of the center squares) -> score 1
                const statsAfterMove = Scanner.getDetailedMoveStats(chess, 'w');

                return { start: statsStart, after: statsAfterMove };
            }
        """)

        print(f"Stats Start: {result['start']}")
        print(f"Stats After e4: {result['after']}")

        # Validation Logic
        assert result['start']['material'] == 0, f"Expected material 0, got {result['start']['material']}"
        assert result['start']['center'] == 0, f"Expected center 0, got {result['start']['center']}"

        assert result['after']['material'] == 0, "Material should still be 0 (equal)"
        assert result['after']['center'] == 1, f"Expected center 1 after e4, got {result['after']['center']}"

        print("Logic verification passed!")

        # 4. Take a screenshot just to prove page loaded
        page.screenshot(path="verification/logic_verified.png")
        print("Screenshot saved.")

        browser.close()

if __name__ == "__main__":
    verify_logic()
