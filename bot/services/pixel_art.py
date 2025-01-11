def increase_pixelation(image_bytes: bytes) -> bytes:
    """
    Increase block size for pixelation. 
    Example placeholder: In reality, parse image_bytes to a pixel array, block it, encode back.
    """
    # TODO: your manual image-processing code
    return image_bytes

def decrease_pixelation(image_bytes: bytes) -> bytes:
    """
    Decrease block size.
    """
    return image_bytes

def apply_color_count(image_bytes: bytes, num_colors: int = 16) -> bytes:
    """
    Naive color quantization to `num_colors`.
    """
    return image_bytes

def apply_bw(image_bytes: bytes) -> bytes:
    """
    Convert the image to grayscale (R=G=B).
    """
    return image_bytes
