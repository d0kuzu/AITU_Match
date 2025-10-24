import asyncio
import json

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove

from config.config import Environ
from database.models.profile import Profile
from database.repo import UserRepo, ProfileRepo, Repos
from services.helpers.send_photos import send_photos
from telegram.filters.registration import RegisteredFilter
from telegram.handlers.menu import show_menu
from telegram.misc.consts import specializations
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.paths import PATHS
from telegram.misc.states import WelcomeStatesGroup, CreateProfileStates, MenuStates
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(not RegisteredFilter())

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer_photo(
        photo=FSInputFile(PATHS.welcome_photo),
        caption=TEXTS.welcome_texts.welcome_text,
        reply_markup=ReplyKeyboards.welcome_keyboard(),
        parse_mode="Markdown",
    )

    await state.set_state(WelcomeStatesGroup.ask_barcode)


@router.message(WelcomeStatesGroup.ask_barcode)
async def user_barcode(message: Message, state: FSMContext):
    await message.answer(TEXTS.welcome_texts.text_main_menu)
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(1)

    await message.answer(TEXTS.welcome_texts.ask_barcode)

    await state.set_state(WelcomeStatesGroup.wait_barcode)


@router.message(WelcomeStatesGroup.wait_barcode)
async def wait_user_barcode(message: Message, state: FSMContext, repos: Repos):
    if message.text and message.text.isdigit():
        if len(message.text) == 6 and await repos.barcode.is_exist(message.text):
            if not await repos.user.is_user_exist_by_barcode(message.text):
                try:
                    await repos.user.create(message.from_user.id, int(message.text))

                    await state.set_state(WelcomeStatesGroup.welcome)
                    await message.answer("Welcome to the club, buddy!")
                    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Error during user registration: {e}")
                    await state.clear()
                    await message.answer("Произошла ошибка при регистрации. Попробуйте еще раз.")
            else:
                await message.answer("Этот barcode уже занят")
        elif len(message.text) == 6:
            await message.answer("Данный barcode отсутствует в базе (вероятнее всего вы не студент AITU)")
        else:
            await message.answer("Твой barcode неверен!")
    else:
        await message.answer("Barcode должен быть числом!")


@router.message(WelcomeStatesGroup.welcome)
async def profile_create_start(message: Message, state: FSMContext):
    await message.answer(TEXTS.profile_texts.start_profile_create)
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(2)

    await message.answer(TEXTS.profile_texts.profile_create_name)

    await state.set_state(CreateProfileStates.name)


@router.message(CreateProfileStates.name)
async def profile_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            TEXTS.profile_texts.profile_create_mistake,
            reply_markup=ReplyKeyboardRemove()
        )
    elif len(message.text) < 2 or len(message.text) > 64:
        await message.answer(
            TEXTS.profile_texts.profile_create_name_length,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(name=message.text)
        await message.answer(
            TEXTS.profile_texts.profile_create_age.format(name=message.text),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(CreateProfileStates.age)


@router.message(CreateProfileStates.age)
async def profile_age(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(
            TEXTS.profile_texts.profile_create_mistake,
            reply_markup=ReplyKeyboardRemove()
        )
    elif not message.text.isdigit():
        await message.answer(
            TEXTS.profile_texts.profile_create_age_str,
            reply_markup=ReplyKeyboardRemove()
        )
    elif int(message.text) < 16 or int(message.text) > 35:
        await message.answer(
            TEXTS.profile_texts.profile_create_age_strange,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(age=int(message.text))
        await message.answer(
            TEXTS.profile_texts.profile_create_sex.format(age=message.text),
            reply_markup=ReplyKeyboards.choose_sex()
        )
        await state.set_state(CreateProfileStates.sex)


@router.message(CreateProfileStates.sex)
async def profile_sex(message: Message, state: FSMContext):
    if message.text not in [TEXTS.profile_texts.profile_create_sex_male, TEXTS.profile_texts.profile_create_sex_female]:
        await message.answer(
            TEXTS.profile_texts.profile_create_mistake,
            reply_markup=ReplyKeyboards.choose_sex()
        )
    else:
        if message.text == TEXTS.profile_texts.profile_create_sex_female:
            await state.update_data(sex='female')
        else:
            await state.update_data(sex='male')

        await message.answer(
            TEXTS.profile_texts.profile_create_opposite_sex,
            reply_markup=ReplyKeyboards.choose_opposite_sex(),
        )
        await state.set_state(CreateProfileStates.opposite_sex)


@router.message(CreateProfileStates.opposite_sex)
async def profile_opposite_sex(message: Message, state: FSMContext):
    sexes = [TEXTS.profile_texts.profile_create_opposite_sex_males, TEXTS.profile_texts.profile_create_opposite_sex_females, TEXTS.profile_texts.profile_create_opposite_sex_both]
    if message.text not in sexes:
        await message.answer(
            TEXTS.profile_texts.profile_create_mistake,
            reply_markup=ReplyKeyboards.choose_sex()
        )
    else:
        if message.text == sexes[1]:
            await state.update_data(opposite_sex='females')
        elif message.text == sexes[0]:
            await state.update_data(opposite_sex='males')
        else:
            await state.update_data(opposite_sex='both')

        await message.answer(
            TEXTS.profile_texts.profile_create_uni,
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.university)


@router.message(CreateProfileStates.university)
async def profile_university(message: Message, state: FSMContext):
    if message.text.upper() not in specializations:
        await message.answer(
            TEXTS.profile_texts.profile_create_cant_find.format(specializations=", ".join(specializations)),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(uni=message.text.upper())
        await message.answer(
            TEXTS.profile_texts.profile_create_description,
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(CreateProfileStates.description)


@router.message(CreateProfileStates.description)
async def profile_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        TEXTS.profile_texts.profile_create_photo,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CreateProfileStates.photo)


@router.message(CreateProfileStates.photo, F.text == TEXTS.profile_texts.profile_create_photo_save)
async def save_profile_photos(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_value("photos", [])

    s3paths = []
    if len(data) >= 1:
        for i, msg in enumerate(data):
            dest_path = PATHS.user_photo_dir / f"{message.from_user.id}_N{i + 1}.jpg"
            await message.bot.download(msg, destination=dest_path)
            s3paths.append(str(dest_path))
    elif len(data) == 1:
        dest_path = PATHS.user_photo_dir / f"{message.from_user.id}.jpg"
        await message.bot.download(data[-1], destination=dest_path)
        s3paths.append(str(dest_path))
    else:
        await message.answer(TEXTS.profile_texts.profile_create_photo_amount)
        return

    data = await state.get_data()

    profile = await repos.profile.create(message.from_user.id, data, s3paths)

    await send_photos(message, s3paths, f"Анкета создана.\n{profile.name}, {profile.age} лет, {profile.uni}\n{profile.description}")

    await state.set_state(MenuStates.main_menu)
    await show_menu(message)


@router.message(CreateProfileStates.photo)
async def profile_photo(message: Message, state: FSMContext, repos: Repos):
    if not message.photo:
        await message.answer(
            TEXTS.profile_texts.profile_create_photo_error,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        data = await state.get_value("photos", [])
        data.append(message.photo[-1].file_id)
        await state.update_data(photos=data)
        await message.answer(f"Загружено {len(data)}/3", reply_markup=ReplyKeyboards.save_photos())

        if len(data) >= 3:
            await message.answer(TEXTS.profile_texts.profile_create_photo_saving, reply_markup=ReplyKeyboardRemove())
            await save_profile_photos(message, state, repos)
