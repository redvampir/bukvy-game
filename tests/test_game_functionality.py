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


def test_game_interaction():
    """Проверяет базовое взаимодействие с игрой"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('#start')

            # Проверяем начальное состояние
            score = page.locator('#score').inner_text()
            assert score == '0', f"Начальный счёт должен быть 0, получено: {score}"

            mistakes = page.locator('#mistakes').inner_text()
            assert mistakes == '0', f"Начальные ошибки должны быть 0, получено: {mistakes}"

            streak = page.locator('#streak').inner_text()
            assert streak == '0', f"Начальная серия должна быть 0, получено: {streak}"

            accuracy = page.locator('#accuracy').inner_text()
            assert accuracy == '100%', f"Начальная точность должна быть 100%, получено: {accuracy}"

            # Нажимаем старт
            page.click('#start')
            time.sleep(0.5)

            # Проверяем что буква появилась
            target = page.locator('#target').inner_text()
            assert target != '—', "После старта должна появиться буква"
            assert len(target) == 1, f"Должна быть одна буква, получено: {target}"

            browser.close()
            print("✅ Базовое взаимодействие работает корректно")
    finally:
        stop_server(proc)


def test_theme_toggle():
    """Проверяет переключение темы"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.theme-toggle')

            # Проверяем начальную тему (светлая)
            body_class = page.locator('body').get_attribute('class')
            initial_dark = 'dark-theme' in (body_class or '')

            # Переключаем тему
            page.click('.theme-toggle')
            time.sleep(0.3)

            # Проверяем что тема изменилась
            body_class_after = page.locator('body').get_attribute('class')
            after_dark = 'dark-theme' in (body_class_after or '')
            assert initial_dark != after_dark, "Тема должна измениться после клика"

            # Переключаем обратно
            page.click('.theme-toggle')
            time.sleep(0.3)

            body_class_final = page.locator('body').get_attribute('class')
            final_dark = 'dark-theme' in (body_class_final or '')
            assert initial_dark == final_dark, "Тема должна вернуться к исходной"

            browser.close()
            print("✅ Переключение темы работает корректно")
    finally:
        stop_server(proc)


def test_sound_toggle():
    """Проверяет переключение звука"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('.sound-toggle')

            # Проверяем начальное состояние
            initial_class = page.locator('.sound-toggle').get_attribute('class')
            initial_muted = 'muted' in (initial_class or '')

            # Переключаем звук
            page.click('.sound-toggle')
            time.sleep(0.2)

            # Проверяем что состояние изменилось
            after_class = page.locator('.sound-toggle').get_attribute('class')
            after_muted = 'muted' in (after_class or '')
            assert initial_muted != after_muted, "Состояние звука должно измениться"

            browser.close()
            print("✅ Переключение звука работает корректно")
    finally:
        stop_server(proc)


def test_difficulty_change():
    """Проверяет смену уровня сложности"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('#set')

            # Меняем на гласные
            page.select_option('#set', 'vowels')
            time.sleep(0.2)

            # Проверяем что подсказка обновилась
            hint_text = page.locator('#hintLetters').inner_text()
            assert 'А' in hint_text, "Должна быть буква А в подсказке"

            # Меняем на все буквы
            page.select_option('#set', 'all')
            time.sleep(0.2)

            hint_text_all = page.locator('#hintLetters').inner_text()
            # Проверяем что в списке стало больше букв
            assert len(hint_text_all) > len(hint_text), \
                "При выборе 'все буквы' должно быть больше букв в подсказке"

            browser.close()
            print("✅ Смена уровня сложности работает корректно")
    finally:
        stop_server(proc)


def test_reset_button():
    """Проверяет кнопку сброса"""
    proc = start_server()
    url = f"http://localhost:{SERVER_PORT}/bukvy.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_selector('#reset')

            # Запускаем игру
            page.click('#start')
            time.sleep(0.5)

            # Нажимаем сброс
            page.click('#reset')
            time.sleep(0.3)

            # Проверяем что все обнулилось
            score = page.locator('#score').inner_text()
            assert score == '0', f"После сброса счёт должен быть 0, получено: {score}"

            target = page.locator('#target').inner_text()
            assert target == '—', f"После сброса должно быть '—', получено: {target}"

            browser.close()
            print("✅ Кнопка сброса работает корректно")
    finally:
        stop_server(proc)
