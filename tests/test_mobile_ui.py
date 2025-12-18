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
    time.sleep(0.8)
    return proc


def stop_server(proc):
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        proc.kill()


def test_mobile_elements_fit():
    """Проверяет что все элементы помещаются на мобильном экране"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.card')

            card_el = page.query_selector('.card')
            card_box = card_el.bounding_box()
            card_width = card_box['width']
            padding = 20

            # Проверяем селект
            select_el = page.query_selector('#set')
            select_box = select_el.bounding_box()
            assert select_box['width'] <= card_width - padding, \
                f"Select выходит за границы: {select_box['width']} > {card_width - padding}"

            # Проверяем чекбокс и его label
            checkbox_pill = page.query_selector('.toggle-pill')
            checkbox_box = checkbox_pill.bounding_box()
            assert checkbox_box['width'] <= card_width - padding, \
                f"Чекбокс выходит за границы: {checkbox_box['width']} > {card_width - padding}"

            # Проверяем прогресс-бар
            progress_el = page.query_selector('.progress-container')
            progress_box = progress_el.bounding_box()
            assert progress_box['width'] <= card_width - padding, \
                f"Прогресс-бар выходит за границы: {progress_box['width']} > {card_width - padding}"

            # Проверяем кнопки
            buttons = page.query_selector_all('.row button')
            for btn in buttons:
                btn_box = btn.bounding_box()
                assert btn_box['x'] >= card_box['x'], "Кнопка выходит слева"
                assert btn_box['x'] + btn_box['width'] <= card_box['x'] + card_width, "Кнопка выходит справа"

            context.close()
            browser.close()
            print("✅ Все элементы помещаются на мобильном экране")
    finally:
        stop_server(proc)


def test_mobile_grid_layout():
    """Проверяет что сетка букв правильно отображается на мобильном"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.grid')

            # Проверяем что сетка имеет 3 колонки на мобильном
            grid_el = page.query_selector('.grid')
            computed = page.evaluate("""(el) => {
                const styles = window.getComputedStyle(el);
                return styles.gridTemplateColumns;
            }""", grid_el)
            
            # На мобильном должно быть 3 колонки (проверяем количество значений)
            columns = computed.split()
            assert len(columns) == 3, f"На мобильном должно быть 3 колонки, получено: {len(columns)} ({computed})"

            # Проверяем что плитки достаточно большие для тапа
            tiles = page.query_selector_all('.tile')
            assert len(tiles) > 0, "Плитки не найдены"
            
            first_tile_box = tiles[0].bounding_box()
            min_tap_size = 40  # минимальный размер для комфортного тапа
            assert first_tile_box['width'] >= min_tap_size, \
                f"Плитки слишком маленькие для тапа: {first_tile_box['width']} < {min_tap_size}"
            assert first_tile_box['height'] >= min_tap_size, \
                f"Плитки слишком маленькие для тапа: {first_tile_box['height']} < {min_tap_size}"

            context.close()
            browser.close()
            print("✅ Сетка букв корректно отображается на мобильном")
    finally:
        stop_server(proc)


def test_mobile_buttons_accessible():
    """Проверяет что кнопки достаточно большие для тапа"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('button')

            # Минимальный размер кнопки для комфортного тапа (32px приемлемо для мобильных)
            min_button_height = 30

            buttons = page.query_selector_all('button')
            for btn in buttons:
                btn_box = btn.bounding_box()
                assert btn_box['height'] >= min_button_height, \
                    f"Кнопка слишком маленькая: {btn_box['height']} < {min_button_height}"

            # Проверяем toggle-кнопки (тема и звук)
            theme_toggle = page.query_selector('.theme-toggle')
            sound_toggle = page.query_selector('.sound-toggle')
            
            for toggle in [theme_toggle, sound_toggle]:
                toggle_box = toggle.bounding_box()
                min_toggle_size = 40
                assert toggle_box['width'] >= min_toggle_size, \
                    f"Toggle кнопка слишком маленькая: {toggle_box['width']} < {min_toggle_size}"

            context.close()
            browser.close()
            print("✅ Все кнопки достаточно большие для тапа")
    finally:
        stop_server(proc)


def test_mobile_achievements_visible():
    """Проверяет что достижения видны на мобильном"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.achievements')

            achievements_el = page.query_selector('.achievements')
            achievements_box = achievements_el.bounding_box()
            
            # Проверяем что достижения видны (имеют высоту)
            assert achievements_box['height'] > 0, "Достижения не видны"

            # Проверяем что каждое достижение достаточно большое
            achievement_items = page.query_selector_all('.achievement')
            assert len(achievement_items) > 0, "Иконки достижений не найдены"
            
            for item in achievement_items:
                item_box = item.bounding_box()
                assert item_box['width'] >= 20, f"Иконка достижения слишком маленькая: {item_box['width']}"

            context.close()
            browser.close()
            print("✅ Достижения корректно отображаются на мобильном")
    finally:
        stop_server(proc)


def test_mobile_history_visible():
    """Проверяет что история ответов видна на мобильном"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport={"width": 360, "height": 800}, is_mobile=True)
            page = context.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.history')

            history_el = page.query_selector('.history')
            history_box = history_el.bounding_box()
            
            # История должна иметь минимальную высоту (даже если пустая)
            assert history_box['height'] >= 30, \
                f"История слишком маленькая: {history_box['height']}"

            card_el = page.query_selector('.card')
            card_box = card_el.bounding_box()
            
            # История не должна выходить за пределы карточки
            assert history_box['width'] <= card_box['width'], \
                f"История выходит за границы карточки: {history_box['width']} > {card_box['width']}"

            context.close()
            browser.close()
            print("✅ История ответов корректно отображается на мобильном")
    finally:
        stop_server(proc)
