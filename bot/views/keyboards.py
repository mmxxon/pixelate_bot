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

    # +, -, Colors Count, B&W
    builder.button(text="+", callback_data="pixel_plus")
    builder.button(text="-", callback_data="pixel_minus")
    builder.button(text="Colors Count", callback_data="pixel_colors")
    builder.button(text="B&W", callback_data="pixel_bw")

    # Toggle between "Preview" and "Save"
    btn_text = "Preview" if preview_stage == 0 else "Save"
    builder.button(text=btn_text, callback_data="pixel_preview")

    # Back to Main
    builder.button(text="Back to Main", callback_data="pixel_back_to_main")

    # e.g., 4 in the first row, 1 in the second, 1 in the third
    builder.adjust(4, 1, 1)

    return builder.as_markup()

#
# BRIGHTNESS MENU
#
def brightness_menu_keyboard(preview_stage: int = 0) -> InlineKeyboardMarkup:
    """
    Brightness menu with +, - and a "Preview" -> "Save" toggle.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="+", callback_data="brightness_plus")
    builder.button(text="-", callback_data="brightness_minus")

    btn_text = "Preview" if preview_stage == 0 else "Save"
    builder.button(text=btn_text, callback_data="brightness_preview")

    # Example layout: 2 buttons in the first row, 1 in the second
    builder.adjust(2, 1)

    return builder.as_markup()

#
# CONTRAST MENU
#
def contrast_menu_keyboard(preview_stage: int = 0) -> InlineKeyboardMarkup:
    """
    Contrast menu with +, - and a "Preview" -> "Save" toggle.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text="+", callback_data="contrast_plus")
    builder.button(text="-", callback_data="contrast_minus")

    btn_text = "Preview" if preview_stage == 0 else "Save"
    builder.button(text=btn_text, callback_data="contrast_preview")

    # Example layout: 2 buttons in the first row, 1 in the second
    builder.adjust(2, 1)

    return builder.as_markup()
