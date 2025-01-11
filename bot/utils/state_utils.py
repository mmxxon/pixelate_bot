from aiogram.fsm.context import FSMContext
from models.user_data import UserData

async def load_user_data(state: FSMContext) -> UserData:
    """
    Loads user data from state, ignoring ephemeral fields like 'pixel_preview_stage'.
    """
    data = await state.get_data()
    # Remove ephemeral keys
    ephemeral_keys = ["pixel_preview_stage", "brightness_preview_stage", "contrast_preview_stage"]
    for key in ephemeral_keys:
        data.pop(key, None)

    # Convert remaining data into UserData
    user_data = UserData(**data) if data else UserData()
    return user_data

async def save_user_data(state: FSMContext, user_data: UserData):
    """Dump user data back into the FSM state."""
    # Convert user_data to dict
    user_data_dict = user_data.__dict__.copy()
    # ephemeral keys are not in user_data_dict anyway
    await state.update_data(**user_data_dict)
