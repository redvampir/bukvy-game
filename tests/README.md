# Тесты для буквенной игры

## Установка зависимостей

```bash
pip install -r requirements-dev.txt
playwright install chromium
```

## Запуск тестов

Запуск всех тестов:
```bash
pytest -v
```

Запуск конкретного теста:
```bash
pytest tests/test_mobile_ui.py -v
pytest tests/test_game_functionality.py -v
pytest tests/test_mobile_select.py -v
```

## Описание тестов

### test_mobile_select.py
- `test_select_fits_mobile` - проверяет, что селект не выходит за границы карточки на мобильном

### test_mobile_ui.py
- `test_mobile_elements_fit` - все элементы помещаются на мобильном экране
- `test_mobile_grid_layout` - сетка букв имеет 3 колонки на мобильном
- `test_mobile_buttons_accessible` - кнопки достаточно большие для тапа
- `test_mobile_achievements_visible` - достижения корректно отображаются
- `test_mobile_history_visible` - история ответов видна и не выходит за границы

### test_game_functionality.py
- `test_game_interaction` - базовое взаимодействие с игрой (старт, счёт, буквы)
- `test_theme_toggle` - переключение светлой/темной темы
- `test_sound_toggle` - переключение звука
- `test_difficulty_change` - смена уровня сложности
- `test_reset_button` - сброс игры

## Покрытие

✅ Мобильная адаптация  
✅ Базовая функциональность  
✅ Переключатели и настройки  
✅ UI элементы

Всего: 11 тестов
