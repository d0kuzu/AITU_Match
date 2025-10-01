import json
from pathlib import Path

from aiogram import F, Bot, Router
from aiogram.types import Message, FSInputFile, KeyboardButton, ReplyKeyboardMarkup, InputMediaPhoto, \
    ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.repository.types import SexEnum
from src.service.send_photo import send_photos
from src.states import UserRoadmap, EditProfileStates
from src.keyboards.reply import main_menu_keyboard, photo_collect
from src.service.db_service import ServiceDB
from src.service.schemas import ProfileCreateInternalSchema
from src.static.text import texts
from src.static.text.texts import text_male, text_female, text_main_menu

edit_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR_EDIT = BASE_DIR / "static" / "users"
UPLOAD_DIR_EDIT.mkdir(parents=True, exist_ok=True)

TEXT_SKIP_BUTTON = "Оставить как есть ⏭️"

def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXT_SKIP_BUTTON)]], resize_keyboard=True, one_time_keyboard=True)

def sex_selection_horizontal_keyboard_with_skip() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_male), KeyboardButton(text=text_female)],
            [KeyboardButton(text=TEXT_SKIP_BUTTON)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


@edit_router.message(EditProfileStates.start)
async def edit_profile_start(message: Message, state: FSMContext, bot: Bot):
    current_profile = await ServiceDB.get_profile_by_tgid(message.from_user.id)
    if not current_profile:
        await message.answer("Сначала нужно создать анкету...", reply_markup=main_menu_keyboard())
        await state.clear()
        return

    await state.update_data(
        original_name=current_profile.name,
        original_age=current_profile.age,
        original_sex=current_profile.sex,
        original_uni=current_profile.uni,
        original_description=current_profile.description,
        original_s3_path=current_profile.s3_path
    )
    
    await message.answer(
        f"Начинаем редактирование. Текущее имя: {current_profile.name}. Введите новое или нажмите 'Оставить как есть'.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.name)


@edit_router.message(EditProfileStates.name)
async def edit_profile_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(name=data["original_name"])
    elif not message.text:
        await message.answer("Это не похоже на имя. Попробуй еще раз или оставь как есть.", reply_markup=skip_keyboard())
        return
    elif len(message.text) < 2 or len(message.text) > 64:
        await message.answer("Слишком длинное или короткое имя! Давай по новой или оставь как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(name=message.text)

    updated_data = await state.get_data()
    await message.answer(
        f"Имя обновлено на: {updated_data['name']}. Текущий возраст: {data['original_age']}. Введите новый или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.age)


@edit_router.message(EditProfileStates.age)
async def edit_profile_age(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(age=data["original_age"])
    elif not message.text or not message.text.isdigit():
        await message.answer("Это точно число? Попробуй еще раз или оставь как есть.", reply_markup=skip_keyboard())
        return
    elif int(message.text) < 16 or int(message.text) > 60:
        await message.answer("Странный возраст... Подумай еще или оставь как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(age=int(message.text))
    
    updated_data = await state.get_data()
    await message.answer(
        f"Возраст обновлен на: {updated_data['age']}. Текущий пол: {"Мужской" if data['original_sex'] == SexEnum.MALE else "Женский"}. Выберите новый или оставьте как есть.",
        reply_markup=sex_selection_horizontal_keyboard_with_skip()
    )
    await state.set_state(EditProfileStates.sex)


@edit_router.message(EditProfileStates.sex)
async def edit_profile_sex(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(sex=data["original_sex"])
    elif message.text not in [text_female, text_male]:
        await message.answer("Выберите пол из предложенных или оставьте как есть.", reply_markup=sex_selection_horizontal_keyboard_with_skip())
        return
    else:
        await state.update_data(sex='female' if message.text == text_female else 'male')

    updated_data = await state.get_data()
    await message.answer(
        f"Пол обновлен на: {"Мужской" if updated_data['sex'] == SexEnum.MALE else "Женский"}. Текущая специальность: {data['original_uni']}. Введите новую или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.university)


@edit_router.message(EditProfileStates.university)
async def edit_profile_university(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(uni=data["original_uni"])
    elif message.text.upper() not in ["SE", "MT", "CB", "BDA", "MCS", "BDH", "CS", "SST", "ST", "DT", "DPA", "AB", "IE", "IM", "DTNPE", "IIT", "EE"]:
        await message.answer("Такой специальности нет в списке. Попробуйте еще раз или оставьте как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(uni=message.text.upper())

    updated_data = await state.get_data()
    await message.answer(
        f"Специальность обновлена на: {updated_data['uni']}. Текущее описание: \"{data['original_description']}\". Напишите новое или оставьте как есть.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(EditProfileStates.description)


@edit_router.message(EditProfileStates.description)
async def edit_profile_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == TEXT_SKIP_BUTTON:
        await state.update_data(description=data["original_description"])
    elif not message.text:
        await message.answer("Пустое описание? Попробуйте еще раз или оставьте как есть.", reply_markup=skip_keyboard())
        return
    elif len(message.text) > 1024:
        await message.answer("Слишком длинное описание! Максимум 1024 символа. Попробуйте еще раз или оставьте как есть.", reply_markup=skip_keyboard())
        return
    else:
        await state.update_data(description=message.text)
    
    updated_data = await state.get_data()
    await message.answer(
        f"Описание обновлено. Текущие фото: (отправлю их следующим сообщением).\nОтправьте новые фото (до 3х) или нажмите 'Оставить как есть'.",
        reply_markup=skip_keyboard()
    )

    if data.get("original_s3_path"):
        s3Paths = json.loads(data["original_s3_path"])

        await send_photos(message, s3Paths, "Текущие фото")

    await state.set_state(EditProfileStates.photo)


@edit_router.message(EditProfileStates.photo, F.text == texts.save_photos)
async def edit_profile_photo(message: Message, state: FSMContext, is_skipped=False):
    data = await state.get_data()
    photos = data.get("photos", [])

    s3paths = []
    if len(photos) >= 1:
        for i, msg in enumerate(photos):
            dest_path = UPLOAD_DIR_EDIT / f"{message.from_user.id}_N{i + 1}.jpg"
            await message.bot.download(msg, destination=dest_path)
            s3paths.append(str(dest_path))
    elif len(photos) == 1:
        dest_path = UPLOAD_DIR_EDIT / f"{message.from_user.id}.jpg"
        await message.bot.download(photos[-1], destination=dest_path)
        s3paths.append(str(dest_path))
    if is_skipped:
        s3paths = json.loads(data.get("original_s3_path"))

    await state.update_data(s3_path=json.dumps(s3paths))
    
    updated_data = await state.get_data()

    profile_update_schema = ProfileCreateInternalSchema(
        tg_id=message.from_user.id,
        name=updated_data["name"],
        age=updated_data["age"],
        sex=updated_data["sex"],
        uni=updated_data["uni"],
        description=updated_data["description"],
        s3_path=updated_data["s3_path"],
    )

    try:
        await ServiceDB.update_profile(profile_update_schema)
    except Exception as e:
        print(f"ERROR during profile photo edit: {e}")
        await message.answer(f"Хмм, странно... Что-то нехорошее произошло...", reply_markup=main_menu_keyboard())
        await state.set_state(UserRoadmap.main_menu)
        return

    caption_text = (
        f"Анкета обновлена!\n"
        f"Имя: {profile_update_schema.name}\n"
        f"Возраст: {profile_update_schema.age}\n"
        f"Пол: {"Мужской" if profile_update_schema.sex == SexEnum.MALE else "Женский"}\n"
        f"Специальность: {profile_update_schema.uni}\n"
        f"Описание: {profile_update_schema.description}"
    )

    if updated_data["s3_path"]:
        try:
            s3Paths = json.loads(updated_data["s3_path"])
            print(s3Paths)

            await send_photos(message, s3Paths, caption_text)
        except Exception as e:
            print(f"Error sending final photo: {e}")
            await message.answer(caption_text + "\n\n(Не удалось загрузить фото для показа)", reply_markup=main_menu_keyboard())
    else:
        await message.answer(caption_text + "\n\n(Фото не установлено)", reply_markup=main_menu_keyboard())


    await state.clear()
    await state.set_state(UserRoadmap.main_menu)
    await message.answer(
        "Вернемся в меню! \n" + text_main_menu,
        reply_markup=main_menu_keyboard(),
    )


@edit_router.message(EditProfileStates.photo)
async def profile_photo(message: Message, state: FSMContext):
    if message.text == TEXT_SKIP_BUTTON:
        await edit_profile_photo(message, state, True)

    if not message.photo:
        await message.answer(
            "Это не фото. Отправьте фото или оставьте старое.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        data = await state.get_value("photos", [])
        data.append(message.photo[-1].file_id)
        await state.update_data(photos=data)
        await message.answer(f"Загружено {len(data)}/3", reply_markup=photo_collect())

        if len(data) >= 3:
            await message.answer("Сохрняем эти фото", reply_markup=ReplyKeyboardRemove())
            await edit_profile_photo(message, state, False)
