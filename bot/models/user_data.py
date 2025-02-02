# models/user_data.py

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class UserData:
    base_image_data: Optional[bytes] = None
    current_image_data: Optional[bytes] = None
    
    undo_stack: List[bytes] = field(default_factory=list)
    redo_stack: List[bytes] = field(default_factory=list)

    image_message_id: int = -1
    menu_message_id: int = -1

    # Pixelation
    pixel_size: int = 1
    pixelate_preview_stage: int = 0
    
    # Brightness
    brightness_value: int = 0
    brightness_preview_stage: int = 0
    
    # Contrast
    contrast_value: int = 0
    contrast_preview_stage: int = 0

    # Temporary storage for any preview image
    preview_image_data: Optional[bytes] = None

    new_image_bytes: Optional[bytes] = None

    def push_undo_data(self, new_image: bytes):
        if self.current_image_data is not None:
            self.undo_stack.append(self.current_image_data)
        self.current_image_data = new_image
        self.redo_stack.clear()
        print(len(self.undo_stack))
        print(len(self.redo_stack))

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        if self.current_image_data:
            self.redo_stack.append(self.current_image_data)
        self.current_image_data = self.undo_stack.pop()
        print(len(self.undo_stack))
        print(len(self.redo_stack))
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        if self.current_image_data:
            self.undo_stack.append(self.current_image_data)
        self.current_image_data = self.redo_stack.pop()
        print(len(self.undo_stack))
        print(len(self.redo_stack))
        return True
