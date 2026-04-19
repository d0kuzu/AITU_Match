from itertools import chain

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.repo import Repos
from telegram.filters.role import AdminFilter
from telegram.misc.states import AdminBarcodeStates, AdminActionsStates, AdminBanStates

router = Router()
router.message.filter(AdminFilter())

@router.message(Command("test"))
async def add_barcodes_start(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(data.get("last_activity"))

@router.message(Command("add_barcodes"))
async def add_barcodes_start(message: Message, state: FSMContext):
    await state.set_state(AdminBarcodeStates.wait_barcodes)
    await message.answer("Отправьте баркоды в формате '111111,222222' \n\n-без пробелв \n-баркод свободен \n-длина баркода 6 цифр")


@router.message(Command("clear_actions"))
async def clear_actions_start(message: Message, state: FSMContext):
    await state.set_state(AdminActionsStates.wait_username)
    await message.answer("Отправьте юзернейм пользователя которому хотите обнулить действия \nпример:@gileckos")


@router.message(Command("ban"))
async def ban_user_start(message: Message, state: FSMContext):
    await state.set_state(AdminBanStates.wait_user_id)
    await message.answer("Отправьте user_id пользователя которого хотите забанить")


@router.message(Command("unban"))
async def unban_user_start(message: Message, state: FSMContext):
    await state.set_state(AdminBanStates.wait_unban_user_id)
    await message.answer("Отправьте user_id пользователя которого хотите разбанить")


@router.message(Command("complaints"))
async def list_complaints(message: Message, repos: Repos):
    complaints = await repos.complaint.get_all()
    if not complaints:
        await message.answer("Жалоб пока нет.")
        return

    text = "Список жалоб:\n\n"
    for complaint in complaints:
        target = complaint.target_profile
        username = f"@{target.username}" if target and target.username else f"ID: {complaint.target_id}"
        text += f"Кому: {username}\nПричина: {complaint.reason}\nКомментарий: {complaint.comment}\nДата: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"

    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            await message.answer(text[x:x+4000])
    else:
        await message.answer(text)

    await repos.complaint.delete_all()
    await message.answer("Все жалобы удалены из базы данных.")


@router.message(AdminBarcodeStates.wait_barcodes)
async def add_barcodes(message: Message, state: FSMContext, repos: Repos):
    barcodes: list[str] = message.text.split(',')

    errored = []
    to_add = []
    for barcode in barcodes:
        if len(barcode) != 6 or not barcode.isdigit():
            errored.append({"code": barcode, "reason": "Invalid barcode"})
            continue
        if await repos.barcode.is_exist(barcode):
            errored.append({"code": barcode, "reason": "Barcode already exists"})
            continue
        to_add.append({"code": barcode})

    await repos.barcode.add_multiple(to_add)
    if len(errored) > 0:
        errored_text = "\n".join([f"{i['code']} - {i['reason']}" for i in errored])
        text = "не принятые баркоды: \n" + errored_text
    else:
        text = "баркоды приняты"

    await message.answer(text)
    await state.clear()


@router.message(AdminActionsStates.wait_username)
async def clear_actions(message: Message, state: FSMContext, repos: Repos):
    username = message.text.replace("@", "")

    profile = await repos.profile.search_by_username(username)
    if not profile:
        await message.answer("профиль с таким юзернеймом отсутствует")
        return

    user_id = profile.user_id
    await repos.action.delete_user_actions(user_id)

    await message.answer("действия успешно удалены")
    await state.clear()


@router.message(Command("loadall"))
async def load_all(message: Message, repos: Repos):
    ids = [{ "code": str(idsin) } for idsin in range(254200, 257500)]

    await message.answer("Начало загрузки баркодов")

    BATCH_SIZE = 500
    for i in range(0, len(ids), BATCH_SIZE):
        batch = ids[i:i + BATCH_SIZE]
        await repos.barcode.add_all(batch)

    await message.answer("Баркоды успешно загружены")


@router.message(AdminBanStates.wait_user_id)
async def ban_user(message: Message, state: FSMContext, repos: Repos):
    if not message.text or not message.text.isdigit():
        await message.answer("User ID должен быть числом")
        return

    user_id = int(message.text)

    await repos.delete_user_completely(user_id)

    await repos.ban.add_ban(user_id)

    await message.answer(f"Пользователь {user_id} успешно удален из всех таблиц и забанен.")
    await state.clear()


@router.message(AdminBanStates.wait_unban_user_id)
async def unban_user(message: Message, state: FSMContext, repos: Repos):
    if not message.text or not message.text.isdigit():
        await message.answer("User ID должен быть числом")
        return

    user_id = int(message.text)

    await repos.ban.remove_ban(user_id)

    await message.answer(f"Пользователь {user_id} успешно разбанен.")
    await state.clear()


@router.message(Command("list_banned"))
async def list_banned(message: Message, repos: Repos):
    banned_users = await repos.ban.get_all_banned()
    if not banned_users:
        await message.answer("Нет забаненных пользователей")
        return

    text = "Забаненные пользователи:\n\n"
    for user_id in banned_users:
        text += f"ID: {user_id}\n"

    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            await message.answer(text[x:x+4000])
    else:
        await message.answer(text)
        