from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import strings


def get_accept_privacy_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for start command"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=strings.BTN_BEGIN_REGISTRATION))
    return builder.as_markup(resize_keyboard=True)


def get_course_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for course selection"""
    builder = ReplyKeyboardBuilder()
    for course in strings.COURSES:
        builder.add(KeyboardButton(text=course))
    builder.add(KeyboardButton(text=strings.BTN_CANCEL))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_skip_photo_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard with skip photo option"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=strings.BTN_SKIP_PHOTO))
    builder.add(KeyboardButton(text=strings.BTN_CANCEL))
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard with just cancel button"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=strings.BTN_CANCEL))
    return builder.as_markup(resize_keyboard=True)


def get_main_menu_keyboard(verification_status: str) -> ReplyKeyboardMarkup:
    """Main menu keyboard based on verification status"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=strings.BTN_VIEW_PROFILE))
    builder.add(KeyboardButton(text=strings.BTN_EDIT_PROFILE))
    builder.add(KeyboardButton(text=strings.BTN_CHOOSE_EVENTS))
    
    # Always show search button
    builder.add(KeyboardButton(text=strings.BTN_BEGIN_SEARCH))
    
    # Show appropriate verification button
    if verification_status == 'not_verified':
        builder.add(KeyboardButton(text=strings.BTN_VERIFY_PROFILE))
    elif verification_status == 'pending':
        builder.add(KeyboardButton(text=strings.BTN_VERIFICATION_PENDING))
    elif verification_status == 'denied':
        builder.add(KeyboardButton(text=strings.BTN_RETRY_VERIFICATION))
    elif verification_status == 'verified':
        builder.add(KeyboardButton(text=strings.BTN_ALREADY_VERIFIED))
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_edit_profile_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for choosing what to edit"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Курс"))
    builder.add(KeyboardButton(text="Направление"))
    builder.add(KeyboardButton(text="Возраст"))
    builder.add(KeyboardButton(text="Имя"))
    builder.add(KeyboardButton(text="Описание"))
    builder.add(KeyboardButton(text="Фото"))
    builder.add(KeyboardButton(text=strings.BTN_CANCEL))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_events_keyboard(selected_events: list = None) -> InlineKeyboardMarkup:
    """Keyboard for selecting events"""
    if selected_events is None:
        selected_events = []
    
    builder = InlineKeyboardBuilder()
    
    for event in strings.EVENT_TYPES:
        checkmark = "✅ " if event in selected_events else ""
        builder.add(InlineKeyboardButton(
            text=f"{checkmark}{event}",
            callback_data=f"event_{event}"
        ))
    
    builder.add(InlineKeyboardButton(
        text="💾 Сохранить",
        callback_data="events_save"
    ))
    
    builder.adjust(2)
    return builder.as_markup()


def get_matching_keyboard(has_previous: bool, has_next: bool) -> ReplyKeyboardMarkup:
    """Keyboard for browsing profiles"""
    builder = ReplyKeyboardBuilder()
    
    row1 = []
    if has_previous:
        row1.append(KeyboardButton(text=strings.BTN_PREVIOUS))
    if has_next:
        row1.append(KeyboardButton(text=strings.BTN_NEXT))
    
    for btn in row1:
        builder.add(btn)
    
    builder.add(KeyboardButton(text=strings.BTN_LIKE))
    builder.add(KeyboardButton(text=strings.BTN_DISLIKE))
    builder.add(KeyboardButton(text=strings.BTN_REPORT))
    builder.add(KeyboardButton(text=strings.BTN_CANCEL))
    
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def get_admin_verification_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin keyboard for verification requests"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=strings.BTN_ADMIN_APPROVE,
        callback_data=f"admin_approve_{user_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=strings.BTN_ADMIN_DENY,
        callback_data=f"admin_deny_{user_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=strings.BTN_ADMIN_BAN,
        callback_data=f"admin_ban_{user_id}"
    ))
    builder.adjust(1)
    return builder.as_markup()

def get_admin_report_keyboard(reported_user_id: int, reporter_user_id: int) -> InlineKeyboardMarkup:
    """Admin keyboard for user reports"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=strings.BTN_ADMIN_BAN_REPORTED,
        callback_data=f"admin_ban_report_{reported_user_id}_{reporter_user_id}"
    ))
    builder.add(InlineKeyboardButton(
        text=strings.BTN_ADMIN_DISMISS_REPORT,
        callback_data=f"admin_dismiss_report_{reported_user_id}_{reporter_user_id}"
    ))
    builder.adjust(1)
    return builder.as_markup()