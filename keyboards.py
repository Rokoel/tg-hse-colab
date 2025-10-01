# keyboards.py
from aiogram import types
from config import STRINGS

def start_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(STRINGS["begin_registration"]))
    return kb

def skip_photo_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(STRINGS["skip_photo"]))
    return kb

def main_profile_keyboard(user_verified: int):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(STRINGS["menu_view_profile"]))
    kb.add(types.KeyboardButton(STRINGS["menu_edit_profile"]))
    if user_verified == 2:
        kb.add(types.KeyboardButton(STRINGS["search_begin"]))
    else:
        # display verification state text as the button
        if user_verified == 1:
            kb.add(types.KeyboardButton(STRINGS["verify_pending"]))
        elif user_verified == 3:
            kb.add(types.KeyboardButton(STRINGS["verify_denied"]))
        else:
            kb.add(types.KeyboardButton(STRINGS["menu_verify_profile"]))
    kb.add(types.KeyboardButton(STRINGS["menu_choose_events"]))
    return kb

def events_keyboard(events: list, selected: list):
    kb = types.InlineKeyboardMarkup()
    for ev in events:
        # callback data must be safe; we assume event names are short
        text = ev + (" ✅" if ev in selected else "")
        kb.add(types.InlineKeyboardButton(text=text, callback_data=f"toggle_event|{ev}"))
    kb.add(types.InlineKeyboardButton("Готово", callback_data="events_done"))
    return kb

def admin_verification_buttons(user_id: int):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(STRINGS["admin_buttons_approve"], callback_data=f"admin_verify|approve|{user_id}"))
    kb.add(types.InlineKeyboardButton(STRINGS["admin_buttons_deny"], callback_data=f"admin_verify|deny|{user_id}"))
    kb.add(types.InlineKeyboardButton(STRINGS["admin_buttons_ban"], callback_data=f"admin_verify|ban|{user_id}"))
    return kb

def search_inline_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("« Prev", callback_data="search_prev"),
        types.InlineKeyboardButton("Next »", callback_data="search_next")
    )
    kb.row(
        types.InlineKeyboardButton(STRINGS["like_button"], callback_data="search_like"),
        types.InlineKeyboardButton(STRINGS["dislike_button"], callback_data="search_dislike")
    )
    return kb
