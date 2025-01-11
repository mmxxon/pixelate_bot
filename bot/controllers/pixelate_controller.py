import io
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext

from models.states import BotStates
from utils.state_utils import load_user_data, save_user_data
from views.keyboards import pixelate_menu_keyboard, main_menu_keyboard
from views.messages import pixelate_menu_caption, main_menu_caption
from services.pixel_art import (
    increase_pixelation,
    decrease_pixelation,
    apply_color_count,
    apply_bw
)

pixelate_router = Router(name="pixelate_router")

@pixelate_router.callback_query(F.data == "menu_pixelate", BotStates.MAIN_MENU)
async def open_pixelate_menu(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    await callback.message.edit_caption(
        caption=pixelate_menu_caption(),
        reply_markup=pixelate_menu_keyboard(preview_stage=0)
    )
    await state.set_state(BotStates.PIXELATE_MENU)
    await callback.answer()

@pixelate_router.callback_query(F.data.in_({"pixel_plus", "pixel_minus", "pixel_colors", "pixel_bw"}), BotStates.PIXELATE_MENU)
async def pixelate_adjust_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)

    # Raw bytes
    current_raw = user_data.current_image_data
    if not current_raw:
        await callback.answer("No image found.")
        return

    # Apply actual pixelation logic from services
    if callback.data == "pixel_plus":
        new_image = increase_pixelation(current_raw)
    elif callback.data == "pixel_minus":
        new_image = decrease_pixelation(current_raw)
    elif callback.data == "pixel_colors":
        new_image = apply_color_count(current_raw, num_colors=16)
    else:  # "pixel_bw"
        new_image = apply_bw(current_raw)

    # push_undo_data
    user_data.push_undo_data(new_image)
    await save_user_data(state, user_data)

    await callback.answer("Pixelation updated in memory. Press Preview to see changes.")

@pixelate_router.callback_query(F.data == "pixel_preview", BotStates.PIXELATE_MENU)
async def pixel_preview_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_data = await load_user_data(state)

    preview_stage = data.get("pixel_preview_stage", 0)
    if preview_stage == 0:
        # 1st press => show preview
        data["pixel_preview_stage"] = 1
        await state.set_data(data)

        raw_bytes = user_data.current_image_data
        file_in_io = io.BytesIO(raw_bytes)
        input_file = FSInputFile(file_in_io, filename="edited.jpg")

        await callback.message.edit_media(
            media=InputMediaPhoto(media=input_file),
            reply_markup=pixelate_menu_keyboard(preview_stage=1)
        )
        await callback.answer("Previewing changes. Press 'Save' to confirm.")
    else:
        # 2nd press => finalize changes, back to main menu
        data.pop("pixel_preview_stage", None)
        await state.set_data(data)

        raw_bytes = user_data.current_image_data
        file_in_io = io.BytesIO(raw_bytes)
        input_file = FSInputFile(file_in_io, filename="edited.jpg")

        can_undo = len(user_data.undo_stack) > 0
        can_redo = len(user_data.redo_stack) > 0

        await callback.message.edit_media(
            media=InputMediaPhoto(media=input_file),
            reply_markup=main_menu_keyboard(can_undo, can_redo)
        )
        await callback.message.edit_caption(main_menu_caption())

        await callback.answer("Changes saved. Returning to Main Menu.")
        await state.set_state(BotStates.MAIN_MENU)

@pixelate_router.callback_query(F.data == "pixel_back_to_main", BotStates.PIXELATE_MENU)
async def pixel_back_to_main_callback(callback: CallbackQuery, state: FSMContext):
    """
    User pressed 'Back to Main' from Pixelate menu
    """
    user_data = await load_user_data(state)
    raw_bytes = user_data.current_image_data

    file_in_io = io.BytesIO(raw_bytes)
    input_file = FSInputFile(file_in_io, filename="edited.jpg")

    can_undo = len(user_data.undo_stack) > 0
    can_redo = len(user_data.redo_stack) > 0

    await callback.message.edit_media(
        media=InputMediaPhoto(media=input_file),
        reply_markup=main_menu_keyboard(can_undo, can_redo)
    )
    await callback.message.edit_caption(main_menu_caption())

    await callback.answer("Back to Main Menu")
    await state.set_state(BotStates.MAIN_MENU)
