from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def view_likes_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мои взаимные лайки ❤️", callback_data="view_my_mutual_likes"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="likes_to_main_menu"),
            ]
        ]
    )


def watch_likes_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть", callback_data="view_who_liked_me")]
        ]
    )
