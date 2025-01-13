import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from models.states import BotStates
from models.user_data import UserData
from utils.state_utils import load_user_data, save_user_data
from views.keyboards import contrast_menu_keyboard, main_menu_keyboard
from views.messages import main_menu_caption

from services.image_utils import (
    decode_jpg_to_array,
    encode_array_to_jpg,
    apply_contrast
)
from aiogram.types import InputMediaPhoto, BufferedInputFile

contrast_router = Router(name="contrast_router")

@contrast_router.callback_query(F.data == "menu_contrast", BotStates.MAIN_MENU)
async def open_contrast_menu(callback: CallbackQuery, state: FSMContext):
    """
    Open contrast menu from the main menu.
    """
    user_data = await load_user_data(state)
    user_data.contrast_preview_stage = 0
    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Contrast: {user_data.contrast_value}\nPress + or - to change, then Preview.",
        reply_markup=contrast_menu_keyboard(preview_stage=0)
    )

    await state.set_state(BotStates.CONTRAST_MENU)
    await callback.answer()

@contrast_router.callback_query(F.data == "contrast_plus", BotStates.CONTRAST_MENU)
async def contrast_plus_callback(callback: CallbackQuery, state: FSMContext):
    """
    Increase contrast (by +10, for example).
    """
    user_data = await load_user_data(state)
    user_data.contrast_value += 10
    user_data.contrast_preview_stage = 0
    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Contrast: {user_data.contrast_value} (unsaved). Press Preview.",
        reply_markup=contrast_menu_keyboard(preview_stage=0)
    )
    await callback.answer()

@contrast_router.callback_query(F.data == "contrast_minus", BotStates.CONTRAST_MENU)
async def contrast_minus_callback(callback: CallbackQuery, state: FSMContext):
    """
    Decrease contrast (by -10, for example).
    """
    user_data = await load_user_data(state)
    user_data.contrast_value -= 10
    user_data.contrast_preview_stage = 0
    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Contrast: {user_data.contrast_value} (unsaved). Press Preview.",
        reply_markup=contrast_menu_keyboard(preview_stage=0)
    )
    await callback.answer()

@contrast_router.callback_query(F.data == "contrast_preview", BotStates.CONTRAST_MENU)
async def contrast_preview_callback(callback: CallbackQuery, state: FSMContext):
    """
    Preview -> Save toggle for contrast.
    """
    user_data = await load_user_data(state)

    if user_data.contrast_preview_stage == 0:
        if not user_data.current_image_data:
            await callback.answer("No current image found.", show_alert=True)
            return
        
        width, height, arr = decode_jpg_to_array(user_data.current_image_data)
        arr2 = apply_contrast(arr, user_data.contrast_value)
        preview_img = encode_array_to_jpg(width, height, arr2)

        user_data.preview_image_data = preview_img
        user_data.contrast_preview_stage = 1
        await save_user_data(state, user_data)

        input_file = BufferedInputFile(preview_img, filename="preview.jpg")
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=input_file,
                caption=f"Contrast: {user_data.contrast_value} (preview)"
            ),
            reply_markup=contrast_menu_keyboard(preview_stage=1)
        )
        await callback.answer()
    else:
        preview_img = user_data.preview_image_data
        if not preview_img:
            await callback.answer("No preview image found.", show_alert=True)
            return

        user_data.push_undo_data(preview_img)
        user_data.contrast_value = 0
        user_data.contrast_preview_stage = 0
        user_data.preview_image_data = None

        await save_user_data(state, user_data)

        can_undo = len(user_data.undo_stack) > 0
        can_redo = len(user_data.redo_stack) > 0
        new_file = BufferedInputFile(user_data.current_image_data, filename="edited.jpg")

        await callback.message.edit_media(
            media=InputMediaPhoto(media=new_file, caption=main_menu_caption()),
            reply_markup=main_menu_keyboard(can_undo, can_redo)
        )
        await state.set_state(BotStates.MAIN_MENU)
        await callback.answer()

@contrast_router.callback_query(F.data == "contrast_back_to_main", BotStates.CONTRAST_MENU)
async def contrast_back_to_main_callback(callback: CallbackQuery, state: FSMContext):
    """
    Discard any preview changes.
    """
    user_data = await load_user_data(state)
    user_data.contrast_value = 0
    user_data.contrast_preview_stage = 0
    user_data.preview_image_data = None
    await save_user_data(state, user_data)

    can_undo = len(user_data.undo_stack) > 0
    can_redo = len(user_data.redo_stack) > 0
    new_file = BufferedInputFile(user_data.current_image_data, filename="edited.jpg")

    await callback.message.edit_media(
        media=InputMediaPhoto(media=new_file, caption=main_menu_caption()),
        reply_markup=main_menu_keyboard(can_undo, can_redo)
    )
    await state.set_state(BotStates.MAIN_MENU)
    await callback.answer()
