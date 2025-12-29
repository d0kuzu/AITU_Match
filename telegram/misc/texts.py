from dataclasses import dataclass


@dataclass(frozen=True)
class WelcomeTexts:
    welcome_text: str = """
*Привет, студент!*   

*Aitu MATCH* - это бот для знакомств среди айтушников — находи друзей, единомышленников или даже вторую половинку!  

✨ *Что тут можно делать?*  
• Смотреть анкеты других ребят 🕵🏿‍♂️
• Найти интересных людей 🎓
• Общаться с виртуальным собеседником 🥶 

_Нажми *"Начать"*, чтобы создать свою анкету или посмотреть другие!_ 
"""
    text_main_menu: str = """
    ┏━━━━━━ *AITU MATCH* ━━━━━━┓

      ━━ Знакомься 👱🏿‍♂️

      ━━ Оформи анкету 🎨

    ┗━ *Выбирай кнопку ниже* ━┛
    """
    ask_barcode: str = "Ты еще не зарегестрирован! Введи свой barcode и присоединяйся!"


@dataclass(frozen=True)
class ProfileTexts:
    start_profile_create: str = "Ну что же, давай создадим твою анкету"
    profile_create_caution: str = """
    Во время создания анкеты тебе будут задаваться вопросы.
    Вводи на них ответы и бот 🤖 запомнит твои данные...
    """
    profile_create_mistake: str = "Боюсь ты где-то ошибся, попробуй еще раз"

    profile_create_name: str = "Введи свое имя"
    profile_create_name_length: str = "Слишком длинное или короткое имя! Давай по новой.."

    profile_create_age: str = "Отлично, {name}, теперь твой возраст"
    profile_create_age_str: str = "Странный возраст... Это точно число, не могу понять? Давай еще раз"
    profile_create_age_strange: str = "Странный возраст... Подумай еще"

    profile_create_sex: str = "Отлично, тебе {age} лет, фиксирую. Теперь укажи, ты парень или девушка?"
    profile_create_sex_male = "Парень 🗿"
    profile_create_sex_female = "Девушка 💃"

    profile_create_opposite_sex = "Записал. Теперь скажи кто тебя интересует"
    profile_create_opposite_sex_males = "Парни"
    profile_create_opposite_sex_females = "Девушки"
    profile_create_opposite_sex_both = "Все"

    profile_create_uni = "Записал. Теперь скажи свою специальность"
    profile_create_cant_find = 'Не могу найти такую программу в списке. Попробуй еще раз. \nВот список поддерживаемых: {specializations}'

    profile_create_description = "Напиши о себе: хобби, интересы и увлечения"

    profile_create_photo = "Последний этап! Отправь фото для своей анкеты. Ты можешь прикрепить до 3х фото."
    profile_create_photo_amount = "Нужно отравить хотябы одно фото"
    profile_create_photo_save = "Сохранить фото"
    profile_create_photo_error = "Вряд ли это фотка! Попробуй еще раз"
    profile_create_photo_saving = "Сохраняем эти фото"


@dataclass(frozen=True)
class MenuTexts:
    search_profiles_text: str = "Смотреть анкеты 🔎"
    edit_profile_text: str = "Редактировать свою анкету 🪞"
    want_deactivate: str = "Хочу отключить анкету"
    say_will_wait: str = "Очень жаль \nВсегда буду рад если ты вернешься и активируешь анкету"


@dataclass(frozen=True)
class SearchProfilesTexts:
    like: str = "❤️"
    message: str = "💌"
    skip: str = "👎"
    leave: str = "💤"
    start_search: str = "Начинаем поиск анкет..."


@dataclass(frozen=True)
class NotificationTexts:
    notify_like: str = "Твоя анкета кому-то понравилась. Узнай кто это!"
    notify_likes: str = "Твою анкету лайкнули {count} раз"
    see_likes: str = "Посмотреть"
    start_show: str = "Отлично, подгружаю анкеты..."
    end_show: str = "На этом все"


@dataclass(frozen=True)
class ErrorTexts:
    internal_error: str = "Внутренняя ошибка"


@dataclass(frozen=True)
class EditProfileTexts:
    ask_what_to_edit: str = "Выберите что хотите изменить"
    edit_name: str = "Изменить имя"
    edit_age: str = "Изменить возраст"
    edit_description: str = "Изменить описание"
    edit_images: str = "Изменить фото"
    edit_all: str = "Заполнить анкету заново"
    back_to_menu: str = "Вернутся в меню"
    start_edit_all: str = "Начнем заполнять все с начала"

    updated: str = "Данные обновлены"


@dataclass(frozen=True)
class Texts:
    welcome_texts: WelcomeTexts = WelcomeTexts()
    menu_texts: MenuTexts = MenuTexts()
    profile_texts: ProfileTexts = ProfileTexts()
    search_profiles_texts: SearchProfilesTexts = SearchProfilesTexts()
    notification_texts: NotificationTexts = NotificationTexts()
    error_texts: ErrorTexts = ErrorTexts()
    edit_profile: EditProfileTexts = EditProfileTexts()


TEXTS: Texts = Texts()