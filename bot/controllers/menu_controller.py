import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from models.states import BotStates
from models.user_data import UserData
from views.keyboards import main_menu_keyboard
from views.messages import main_menu_caption
from utils.file_utils import download_photo_to_bytes, send_photo_from_bytes
from utils.state_utils import load_user_data, save_user_data

menu_router = Router(name="menu_router")

@menu_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """
    /start command → initialize user data, ask user to send an image.
    """
    # Create a fresh UserData object in state
    user_data = UserData()
    await save_user_data(state, user_data)
    await message.answer("Welcome! Please send an image to begin editing.")

@menu_router.message(F.photo)
async def handle_new_photo(message: Message, state: FSMContext):
    """
    Handle newly uploaded images. If there's a current image, ask to save or discard.
    """
    user_data = await load_user_data(state)

    if user_data.current_image_data is not None:
        await message.answer("You have an unsaved image. Save previous image? (yes/no)")
        # In a real project, you'd handle the user's yes/no with another handler.

    # Download the new image
    image_bytes = await download_photo_to_bytes(message)
    user_data.base_image_data = image_bytes
    user_data.current_image_data = image_bytes
    user_data.undo_stack.clear()
    user_data.redo_stack.clear()

    await save_user_data(state, user_data)

    # Show main menu
    caption = main_menu_caption()
    menu_markup = main_menu_keyboard(can_undo=False, can_redo=False)
    sent_msg = await send_photo_from_bytes(message, image_bytes, caption=caption, reply_markup=menu_markup)

    # Save message IDs so we can edit or delete later
    user_data.image_message_id = sent_msg.message_id
    user_data.menu_message_id = sent_msg.message_id
    await save_user_data(state, user_data)

    await state.set_state(BotStates.MAIN_MENU)

@menu_router.callback_query(F.data == "undo", BotStates.MAIN_MENU)
async def undo_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    success = user_data.undo()
    await save_user_data(state, user_data)

    if success and user_data.current_image_data:
        can_undo = len(user_data.undo_stack) > 0
        can_redo = len(user_data.redo_stack) > 0

        await callback.message.edit_media(
            media=("photo", user_data.current_image_data),
            reply_markup=main_menu_keyboard(can_undo, can_redo)
        )
        await callback.answer("Undo applied.")
    else:
        await callback.answer("Nothing to undo.", show_alert=True)

@menu_router.callback_query(F.data == "redo", BotStates.MAIN_MENU)
async def redo_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    success = user_data.redo()
    await save_user_data(state, user_data)

    if success and user_data.current_image_data:
        can_undo = len(user_data.undo_stack) > 0
        can_redo = len(user_data.redo_stack) > 0
        await callback.message.edit_media(
            media=("photo", user_data.current_image_data),
            reply_markup=main_menu_keyboard(can_undo, can_redo)
        )
        await callback.answer("Redo applied.")
    else:
        await callback.answer("Nothing to redo.", show_alert=True)

@menu_router.callback_query(F.data == "download_image", BotStates.MAIN_MENU)
async def download_image_callback(callback: CallbackQuery, state: FSMContext):
    user_data = await load_user_data(state)
    if user_data.current_image_data is None:
        await callback.answer("No image to download.", show_alert=True)
        return
    await send_photo_from_bytes(callback.message, user_data.current_image_data, caption="Here is your image.")
    await callback.answer()
