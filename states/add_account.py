from aiogram.fsm.state import State, StatesGroup

class AddAccountState(StatesGroup):
    choosing_category = State()
    entering_login = State()
    entering_password = State()
    entering_price_som = State()
    entering_price_rub = State()
    entering_description = State()
    entering_binding = State()
    uploading_media = State()
    confirming = State()
