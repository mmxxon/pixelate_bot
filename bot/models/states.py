from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    MAIN_MENU = State()
    CONFIRM_SAVE_NEW_IMAGE = State()
    PIXELATE_MENU = State()
    BRIGHTNESS_MENU = State()
    CONTRAST_MENU = State()
    SAVE_MENU = State()