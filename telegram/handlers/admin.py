from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.repo import Repos
from telegram.filters.role import AdminFilter
from telegram.misc.states import AdminBarcodeStates

router = Router()
router.message.filter(AdminFilter())

@router.message(Command("add_barcodes"))
async def add_barcodes_start(message: Message, state: FSMContext):
    await state.set_state(AdminBarcodeStates.wait_barcodes)
    await message.answer("Отправьте баркоды в формате '111111,222222' \n\n-без пробелв \n-баркод свободен \n-длина баркода 6 цифр")

@router.message()
async def add_barcodes(message: Message, repos: Repos):
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