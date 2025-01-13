
import io
from PIL import Image

def decode_jpg_to_array(image_bytes: bytes):
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert('RGB')
        width, height = img.size
        data = list(img.getdata())
        pixel_array = [data[i*width:(i+1)*width] for i in range(height)]
    return width, height, pixel_array

def encode_array_to_jpg(width: int, height: int, pixel_array: list[list[tuple[int,int,int]]]) -> bytes:
    flat_data = []
    for row in pixel_array:
        flat_data.extend(row)
    new_img = Image.new('RGB', (width, height))
    new_img.putdata(flat_data)
    buf = io.BytesIO()
    new_img.save(buf, format='JPEG')
    return buf.getvalue()

def apply_brightness(pixel_array: list[list[tuple[int,int,int]]], brightness_value: int):
    """
    brightness_value > 0 => lighten
    brightness_value < 0 => darken
    """
    if brightness_value == 0:
        return pixel_array

    height = len(pixel_array)
    width = len(pixel_array[0]) if height else 0

    new_array = []
    for row in pixel_array:
        new_row = []
        for (r, g, b) in row:
            nr = max(0, min(255, r + brightness_value))
            ng = max(0, min(255, g + brightness_value))
            nb = max(0, min(255, b + brightness_value))
            new_row.append((nr, ng, nb))
        new_array.append(new_row)
    return new_array

def apply_contrast(pixel_array: list[list[tuple[int,int,int]]], contrast_value: int):
    """
    A simple formula for contrast:
    factor = 1 + (contrast_value / 100)
    new_pixel = (old_pixel - 127.5) * factor + 127.5
    """
    if contrast_value == 0:
        return pixel_array

    factor = 1 + (contrast_value / 100.0)
    height = len(pixel_array)
    width = len(pixel_array[0]) if height else 0

    new_array = []
    for row in pixel_array:
        new_row = []
        for (r, g, b) in row:
            nr = int((r - 127.5) * factor + 127.5)
            ng = int((g - 127.5) * factor + 127.5)
            nb = int((b - 127.5) * factor + 127.5)
            # clamp
            nr = max(0, min(255, nr))
            ng = max(0, min(255, ng))
            nb = max(0, min(255, nb))
            new_row.append((nr, ng, nb))
        new_array.append(new_row)
    return new_array

def pixelate_array(pixel_array, block_size: int):
    if block_size <= 1:
        return pixel_array  # No pixelation
    height = len(pixel_array)
    width = len(pixel_array[0]) if height else 0

    new_array = []
    for row_start in range(0, height, block_size):
        for row_offset in range(block_size):
            if row_start + row_offset >= height:
                break
            new_row = []
            for col_start in range(0, width, block_size):
                block_pixels = []
                for rr in range(row_start, min(row_start + block_size, height)):
                    for cc in range(col_start, min(col_start + block_size, width)):
                        block_pixels.append(pixel_array[rr][cc])
                avg_r = sum(p[0] for p in block_pixels) // len(block_pixels)
                avg_g = sum(p[1] for p in block_pixels) // len(block_pixels)
                avg_b = sum(p[2] for p in block_pixels) // len(block_pixels)
                for _ in range(block_size):
                    if len(new_row) < width:
                        new_row.append((avg_r, avg_g, avg_b))
            new_row = new_row[:width]
            new_array.append(new_row)
    return new_array[:height]
