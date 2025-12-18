import subprocess
import time
import os
import sys
from playwright.sync_api import sync_playwright

SERVER_PORT = 5500
SERVER_CMD = [sys.executable, "-m", "http.server", str(SERVER_PORT)]
SERVER_CWD = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def start_server():
    proc = subprocess.Popen(SERVER_CMD, cwd=SERVER_CWD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # wait a bit
    time.sleep(0.8)
    return proc


def stop_server(proc):
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        proc.kill()


def test_select_fits_mobile():
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('#setToggle')

            # get bounding boxes
            select_el = page.query_selector('#setToggle')
            card_el = page.query_selector('.card')
            assert select_el is not None, "Set toggle element #setToggle not found"
            assert card_el is not None, "Card element .card not found"

            select_box = select_el.bounding_box()
            card_box = card_el.bounding_box()

            print('select_box:', select_box)
            print('card_box:', card_box)

            # Allow small padding tolerance
            padding_tolerance = 8
            assert select_box['width'] <= card_box['width'] - padding_tolerance, \
                f"Set toggle is too wide on mobile: toggle.width={select_box['width']} card.width={card_box['width']}"

            context.close()
            browser.close()
    finally:
        stop_server(proc)
