import io
from aiogram.types import Message, BufferedInputFile

async def download_photo_to_bytes(message: Message) -> bytes:
    file_in_io = io.BytesIO()
    await message.bot.download(
        file=message.photo[-1].file_id,
        destination=file_in_io
    )
    return file_in_io.getvalue()

async def send_photo_from_bytes(message: Message, image_bytes: bytes, caption: str = "", reply_markup=None):
    file_upload = BufferedInputFile(image_bytes, filename="image.jpg")
    return await message.answer_photo(
        photo=file_upload,
        caption=caption,
        reply_markup=reply_markup
    )
