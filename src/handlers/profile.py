import json
from pathlib import Path

from aiogram import F, Bot
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from src.service.send_photo import send_photos
from src.states import UserRoadmap, CreateProfileStates
from src.keyboards.reply import sex_selection_horizontal_keyboard, main_menu_keyboard, photo_collect
from src.service.db_service import ServiceDB
from src.service.schemas import ProfileCreateInternalSchema
from src.static.text import texts
from src.static.text.texts import text_male, text_female, text_main_menu

profile_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "users"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@profile_router.message(CreateProfileStates.start)
async def profile_start(message: Message, state: FSMContext):
    await message.answer(
        "Введи свое имя",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CreateProfileStates.name)


@profile_router.message(CreateProfileStates.name)
async def profile_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif len(message.text) < 2 or len(message.text) > 64:
        await message.answer(
            "Слишком длинное или короткое имя! Давай по новой..",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(name=message.text)
        await message.answer(
            f"Отлично, {message.text}, теперь твой возраст",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(CreateProfileStates.age)


@profile_router.message(CreateProfileStates.age)
async def profile_age(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif not message.text.isdigit():
        await message.answer(
            "Странный возраст... Это точно число, не могу понять? Давай еще раз",
            reply_markup=ReplyKeyboardRemove()
        )
    elif int(message.text) < 16 or int(message.text) > 35:
        await message.answer(
            "Странный возраст... Подумай еще",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(age=int(message.text))
        await message.answer(
            f"Отлично, тебе {message.text} лет, фиксирую. Теперь укажи, ты парень или девушка?",
            reply_markup=sex_selection_horizontal_keyboard()
        )
        await state.set_state(CreateProfileStates.sex)


@profile_router.message(CreateProfileStates.sex)
async def profile_sex(message: Message, state: FSMContext):
    if message.text != text_female and message.text != text_male:
        await message.answer(
            "Боюсь ты где-то ошибся, попробуй еще раз",
            reply_markup=sex_selection_horizontal_keyboard()
        )
    else:
        if message.text == text_female:
            await state.update_data(sex='female')
        else:
            await state.update_data(sex='male')
        await message.answer(
            "Записал. Теперь скажи свою специальность",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.university)


@profile_router.message(CreateProfileStates.university)
async def profile_university(message: Message, state: FSMContext):
    if message.text.upper() not in ["SE", "MT", "CB", "BDA", "MCS", "BDH", "CS", "SST", "ST", "DT", "DPA", "AB", "IE", "IM", "DTNPE", "IIT", "EE"] :
        await message.answer(
            'Не могу найти такую программу в списке. Попробуй еще раз. Вот список поддерживаемых: "SE", "MT", "CB", "BDA", "MCS", "BDH", "CS", "SST", "ST", "DT", "DPA", "AB", "IE", "IM", "DTNPE", "IIT", "EE"',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(uni=message.text.upper())
        await message.answer(
            "Напиши о себе: хобби, интересы и увлечения",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.description)


@profile_router.message(CreateProfileStates.description)
async def profile_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        f"Последний этап! Отправь фото для своей анкеты. Ты можешь прикрепить до 3х фото.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CreateProfileStates.photo)


@profile_router.message(CreateProfileStates.photo, F.text == texts.save_photos)
async def save_profile_photos(message: Message, state: FSMContext):
    data = await state.get_value("photos", [])

    s3paths = []
    if len(data) >= 1:
        for i, msg in enumerate(data):
            dest_path = UPLOAD_DIR / f"{message.from_user.id}_N{i + 1}.jpg"
            await message.bot.download(msg, destination=dest_path)
            s3paths.append(str(dest_path))
    elif len(data) == 1:
        dest_path = UPLOAD_DIR / f"{message.from_user.id}.jpg"
        await message.bot.download(data[-1], destination=dest_path)
        s3paths.append(str(dest_path))
    else:
        await message.answer("Нужно отравить хотябы одно фото")
        return

    data = await state.get_data()
    profile = ProfileCreateInternalSchema(
        tg_id=message.from_user.id,
        name=data["name"],
        age=data["age"],
        sex=data["sex"],
        uni=data["uni"],
        description=data["description"],
        s3_path=json.dumps(s3paths),
    )

    await ServiceDB.add_profile(profile)

    await send_photos(message, s3paths, f"Анкета создана.\n{profile.name}, {profile.age} лет, {profile.uni}\n{profile.description}")

    await state.set_state(UserRoadmap.main_menu)
    await message.answer(
        "Вернемся в меню! \n" + text_main_menu,
        reply_markup=main_menu_keyboard(),
    )


@profile_router.message(CreateProfileStates.photo)
async def profile_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            f"Вряд ли это фотка! Попробуй еще раз",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        data = await state.get_value("photos", [])
        data.append(message.photo[-1].file_id)
        await state.update_data(photos=data)
        await message.answer(f"Загружено {len(data)}/3", reply_markup=photo_collect())

        if len(data) >= 3:
            await message.answer("Сохрняем эти фото", reply_markup=ReplyKeyboardRemove())
            await save_profile_photos(message, state)
