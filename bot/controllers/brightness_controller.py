import io
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext

from models.states import BotStates
from utils.state_utils import load_user_data, save_user_data
from views.keyboards import brightness_menu_keyboard, main_menu_keyboard
from views.messages import brightness_menu_caption, main_menu_caption
from services.image_utils import decode_jpg_to_array, encode_array_to_jpg, apply_brightness

brightness_router = Router(name="brightness_router")

@brightness_router.callback_query(F.data == "menu_brightness", BotStates.MAIN_MENU)
async def open_brightness_menu(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    user_data.brightness_preview_stage = 0
    user_data.preview_image_data = None

    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Brightness: {user_data.brightness_value}\nPress + or - to change, then Preview.",
        reply_markup=brightness_menu_keyboard(preview_stage=0)
    )

    await state.set_state(BotStates.BRIGHTNESS_MENU)
    await callback.answer()

@brightness_router.callback_query(F.data == "brightness_plus", BotStates.BRIGHTNESS_MENU)
async def brightness_plus_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    user_data.brightness_value = min(255, user_data.brightness_value + 10)
    user_data.brightness_preview_stage = 0
    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Brightness: {user_data.brightness_value} (unsaved). Press Preview.",
        reply_markup=brightness_menu_keyboard(preview_stage=0)
    )
    await callback.answer()

@brightness_router.callback_query(F.data == "brightness_minus", BotStates.BRIGHTNESS_MENU)
async def brightness_minus_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    user_data.brightness_value = max(-255, user_data.brightness_value - 10)
    user_data.brightness_preview_stage = 0
    await save_user_data(state, user_data)

    await callback.message.edit_caption(
        caption=f"Brightness: {user_data.brightness_value} (unsaved). Press Preview.",
        reply_markup=brightness_menu_keyboard(preview_stage=0)
    )
    await callback.answer()

@brightness_router.callback_query(F.data == "brightness_preview", BotStates.BRIGHTNESS_MENU)
async def brightness_preview_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)

    if user_data.brightness_preview_stage == 0:
        if not user_data.current_image_data:
            await callback.answer("No current image found.", show_alert=True)
            return
        
        width, height, arr = decode_jpg_to_array(user_data.current_image_data)
        new_arr = apply_brightness(arr, user_data.brightness_value)
        preview_img = encode_array_to_jpg(width, height, new_arr)

        user_data.preview_image_data = preview_img
        user_data.brightness_preview_stage = 1
        await save_user_data(state, user_data)

        input_file = BufferedInputFile(preview_img, filename="preview.jpg")
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=input_file,
                caption=f"Brightness: {user_data.brightness_value} (preview)"
            ),
            reply_markup=brightness_menu_keyboard(preview_stage=1)
        )
        await callback.answer()

    else:
        preview_img = user_data.preview_image_data
        if not preview_img:
            await callback.answer("No preview image found.", show_alert=True)
            return

        user_data.push_undo_data(preview_img)

        user_data.brightness_value = 0
        user_data.brightness_preview_stage = 0
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

@brightness_router.callback_query(F.data == "brightness_back_to_main", BotStates.BRIGHTNESS_MENU)
async def brightness_back_to_main_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    user_data.brightness_value = 0
    user_data.brightness_preview_stage = 0
    user_data.preview_image_data = None
    await save_user_data(state, user_data)

    raw_data = user_data.current_image_data
    new_file = BufferedInputFile(raw_data, filename="edited.jpg")
    can_undo = len(user_data.undo_stack) > 0
    can_redo = len(user_data.redo_stack) > 0

    await callback.message.edit_media(
        media=InputMediaPhoto(media=new_file, caption=main_menu_caption()),
        reply_markup=main_menu_keyboard(can_undo, can_redo)
    )
    await state.set_state(BotStates.MAIN_MENU)
    await callback.answer()
