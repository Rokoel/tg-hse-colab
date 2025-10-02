import os
from typing import Optional
from aiogram.types import Message
import config
import strings


def format_profile(user: dict, show_verification: bool = True) -> str:
    """Format user profile for display"""
    events_str = ", ".join(user['events']) if user['events'] else "Не выбраны"
    
    verification_status_str = ""
    if show_verification:
        status = user['verification_status']
        if status == 'verified':
            verification_status_str = strings.VERIFICATION_STATUS_VERIFIED
        elif status == 'pending':
            verification_status_str = strings.VERIFICATION_STATUS_PENDING
        elif status == 'denied':
            verification_status_str = strings.VERIFICATION_STATUS_DENIED
        else:
            verification_status_str = strings.VERIFICATION_STATUS_NOT_VERIFIED
    
    return strings.PROFILE_TEMPLATE.format(
        name=user['name'],
        course=user['course'],
        program=user['program'],
        age=user['age'],
        description=user['description'],
        events=events_str,
        verification_status=verification_status_str
    )


def validate_age(age_text: str) -> Optional[int]:
    """Validate age input"""
    try:
        age = int(age_text)
        if 16 <= age <= 100:
            return age
    except ValueError:
        pass
    return None


def validate_description(text: str) -> bool:
    """Validate description length"""
    return len(text) <= 500


def get_photo_path(user_id: int, photo_type: str = 'profile') -> str:
    """Get path for storing photo"""
    if photo_type == 'profile':
        return os.path.join(config.PHOTOS_DIR, f"{user_id}.jpg")
    elif photo_type == 'student_id':
        return os.path.join(config.STUDENT_IDS_DIR, f"{user_id}.jpg")
    return ""


async def download_photo(message: Message, user_id: int, photo_type: str = 'profile') -> Optional[str]:
    """Download photo from message and return file_id"""
    if not message.photo:
        return None
    
    photo = message.photo[-1]  # Get highest resolution
    file_id = photo.file_id
    
    # Download the file
    file = await message.bot.get_file(file_id)
    file_path = get_photo_path(user_id, photo_type)
    
    await message.bot.download_file(file.file_path, file_path)
    
    return file_id


def delete_photo(user_id: int, photo_type: str = 'profile'):
    """Delete photo file"""
    file_path = get_photo_path(user_id, photo_type)
    if os.path.exists(file_path):
        os.remove(file_path)


async def send_profile_with_photo(message: Message, user: dict, caption: str):
    """Send profile with photo if available"""
    if user['photo_id']:
        try:
            await message.answer_photo(
                photo=user['photo_id'],
                caption=caption
            )
        except Exception:
            await message.answer(caption)
    else:
        await message.answer(caption)