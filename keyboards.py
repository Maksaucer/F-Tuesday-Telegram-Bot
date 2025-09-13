#keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔞 Получить картинку")],
        [KeyboardButton(text="⚙️ Фильтры")],
        [KeyboardButton(text="❌ Отписаться")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

get_image_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Случайная картинка")],
        [KeyboardButton(text="🕰 Лучшая за период")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

period_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🥉 За день")],
        [KeyboardButton(text="🥈 За неделю")],
        [KeyboardButton(text="🥇 За месяц")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите период"
)