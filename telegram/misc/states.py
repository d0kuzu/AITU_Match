from aiogram.fsm.state import State, StatesGroup


class WelcomeStatesGroup(StatesGroup):
    ask_barcode = State()
    wait_barcode = State()
    welcome = State()


class CreateProfileStates(StatesGroup):
    start = State()
    name = State()
    age = State()
    sex = State()
    opposite_sex = State()
    university = State()
    description = State()
    photo = State()


class SearchProfilesStates(StatesGroup):
    viewing_profile = State()
    wait_message = State()


class SeeLikeNotificationsStates(StatesGroup):
    pending = State()
    viewing_profile = State()


class MenuStates(StatesGroup):
    main_menu = State()
    profile = State()
    deactivated = State()


class EditProfileStates(StatesGroup):
    wait_what_to_edit = State()


class AdminBarcodeStates(StatesGroup):
    wait_barcodes = State()


class AdminActionsStates(StatesGroup):
    wait_username = State()


class ComplainStates(StatesGroup):
    wait_reason = State()
    wait_comment = State()

