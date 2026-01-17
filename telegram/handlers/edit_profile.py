import asyncio
import json
import logging

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from config.enums import FlowEnum
from database.repo import Repos
from services.helpers.send_photos import send_photos
from telegram.handlers import registration
from telegram.handlers.menu import show_menu
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates, EditProfileStates, CreateProfileStates
from telegram.misc.texts import TEXTS

router = Router()

@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.edit_profile_text)
async def ask_what_to_edit(message: Message, state: FSMContext, repos: Repos):
    profile = await repos.profile.search_by_user_id(message.from_user.id)
    if not profile:
        await message.answer("Ошибка показа профиля")
        logging.error(f"ask_what_to_edit, get_profile error {message.from_user.id}")
        return
    await send_photos(message.bot, json.loads(profile.s3_path),
                      f"{profile.name}, {profile.age} лет, {profile.uni.value} - {profile.description}",
                      message.from_user.id)

    await state.set_state(EditProfileStates.wait_what_to_edit)
    await message.answer(TEXTS.edit_profile.ask_what_to_edit, reply_markup=ReplyKeyboards.ask_what_to_edit())
    await state.update_data(flow=FlowEnum.EASY.value)


@router.message(EditProfileStates.wait_what_to_edit, F.text == TEXTS.edit_profile.back_to_menu)
async def back_to_menu(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)
    await show_menu(message, state)


@router.message(EditProfileStates.wait_what_to_edit)
async def start_to_edit(message: Message, state: FSMContext):
    match message.text:
        case TEXTS.edit_profile.edit_name:
            await state.update_data(edit_one=True)

            await message.answer(TEXTS.profile_texts.profile_create_name)

            await state.set_state(CreateProfileStates.name)

        case TEXTS.edit_profile.edit_age:
            await state.update_data(edit_one=True)

            await message.answer(
                TEXTS.edit_profile.ask_new_age,
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(CreateProfileStates.age)

        case TEXTS.edit_profile.edit_description:
            await state.update_data(edit_one=True)

            await message.answer(
                TEXTS.profile_texts.profile_create_description,
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(CreateProfileStates.description)

        case TEXTS.edit_profile.edit_images:
            await state.update_data(edit_one=True)

            await message.answer(
                TEXTS.profile_texts.profile_create_photo,
                reply_markup=ReplyKeyboards.save_photos(),
            )
            await state.set_state(CreateProfileStates.photo)

        case TEXTS.edit_profile.edit_all:
            await message.answer(TEXTS.edit_profile.start_edit_all, reply_markup=ReplyKeyboardRemove())
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

            await asyncio.sleep(1)

            await message.answer(TEXTS.profile_texts.profile_create_name)

            await state.set_state(CreateProfileStates.name)

        case _:
            await message.answer(TEXTS.edit_profile.wrong_button)


async def save_edited_data(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()

    await repos.profile.save_profile(message.from_user.id, data)

    await message.answer(TEXTS.edit_profile.updated, reply_markup=ReplyKeyboardRemove())

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(1)

    await state.set_state(MenuStates.main_menu)
    await show_menu(message, state)

