from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

#
# MAIN MENU
#
def main_menu_keyboard(can_undo: bool, can_redo: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Undo button or dummy
    if can_undo:
        builder.button(text="Undo", callback_data="undo")
    else:
        builder.button(text="Undo (unavailable)", callback_data="noop")

    # Pixelate, Brightness, Contrast
    builder.button(text="Pixelate", callback_data="menu_pixelate")
    builder.button(text="Brightness", callback_data="menu_brightness")
    builder.button(text="Contrast", callback_data="menu_contrast")

    # Redo button or dummy
    if can_redo:
        builder.button(text="Redo", callback_data="redo")
    else:
        builder.button(text="Redo (unavailable)", callback_data="noop")

    # Download
    builder.button(text="Download", callback_data="download_image")

    # Example layout: 5 buttons in the first row, 1 in the second row
    builder.adjust(5, 1)

    return builder.as_markup()

#
# PIXELATE MENU
#
def pixelate_menu_keyboard(preview_stage: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="+", callback_data="pixel_plus")
    builder.button(text="-", callback_data="pixel_minus")
    builder.button(
        text="Preview" if preview_stage == 0 else "Save",
        callback_data="pixel_preview"
    )
    builder.button(text="Back to Main", callback_data="pixel_back_to_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def brightness_menu_keyboard(preview_stage: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="+", callback_data="brightness_plus")
    builder.button(text="-", callback_data="brightness_minus")
    builder.button(
        text="Preview" if preview_stage == 0 else "Save",
        callback_data="brightness_preview"
    )
    builder.button(text="Back to Main", callback_data="brightness_back_to_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def contrast_menu_keyboard(preview_stage: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="+", callback_data="contrast_plus")
    builder.button(text="-", callback_data="contrast_minus")
    builder.button(
        text="Preview" if preview_stage == 0 else "Save",
        callback_data="contrast_preview"
    )
    builder.button(text="Back to Main", callback_data="contrast_back_to_main")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

def confirm_save_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Yes", callback_data="confirm_save_yes")
    builder.button(text="No", callback_data="confirm_save_no")
    builder.adjust(2)
    return builder.as_markup()

