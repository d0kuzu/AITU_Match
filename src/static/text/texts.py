text_main_menu = """
┏━━━━━━ *AITU MATCH* ━━━━━━┓

  ━━ Знакомься 👱🏿‍♂️

  ━━ Оформи анкету 🎨

┗━ *Выбирай кнопку ниже* ━┛
"""


text_main_menu_get_back = [
    "Рад снова тебя видеть! 😈",
    "Зачем ты удалил наш чат!? Ну ладно, заходи, я соскучился 🥹",
    "Какие люди в Голливуде! Проходи!",
    "Залетай ✈️",
]

text_search_profiles_start = "Нажми кнопку для запуска поиска анкет 👇\n(чтобы вернутся в главное меню просто введи любое сообщение)"

text_search_profiles = "Смотреть анкеты 🔎"
text_edit_profile = "Редактировать свою анкету 🪞"
text_show_invite_code = "Инвайт-код для друга 💎"
text_my_likes = "Мои лайки ❤️"
text_go_to_deepseek = "Мне никто не пишет. . ."

text_yes = "Да ✅"
text_no = "Нет ❌"

text_male = "Парень 🗿"
text_female = "Девушка 💃"

text_profile_create_begin = """
Во время создания анкеты тебе будут задаваться вопросы.
Вводи на них ответы и бот 🤖 запомнит твои данные...
"""

save_photos = "Сохранить фото"


def get_invite_message(available_invites: int, invite_code: str) -> str:
    message = f"""
Количество доступных приглашений: *{available_invites}*

Пригласительный код: *{invite_code}*
(после каждой активации этот код меняется)
"""
    return message