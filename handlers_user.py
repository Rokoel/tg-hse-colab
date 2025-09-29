import os
import re
from typing import Dict, Any
from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import STRINGS, BOT_TOKEN
from keyboards import start_keyboard, skip_photo_keyboard, main_profile_keyboard, events_keyboard, search_inline_keyboard
from utils import (validate_course, validate_age, validate_name,
                   validate_description, save_profile_photo, save_id_photo, remove_file)
from db import (create_or_update_user, get_user, set_verification_status,
                save_id_upload, get_verified_pool, list_events, set_user_event,
                clear_user_events, get_user_events, ensure_events, like_user,
                is_mutual, like_user as db_like_user, unlike_user)


router = Router()
bot = Bot(token=BOT_TOKEN)

# --- FSM states for registration & edits ---
class RegStates(StatesGroup):
    COURSE = State()
    DIRECTION = State()
    AGE = State()
    NAME = State()
    DESCRIPTION = State()
    PHOTO = State()
    ID_UPLOAD = State()
    # edit states named in-state strings (kept as before)

# --- In-memory search session storage (not persistent) ---
# Structure: { user_id: { "list": [profiles], "index": int, "seen_ids": set(), "excluded": set() } }
search_sessions: Dict[int, Dict[str, Any]] = {}

# ---------- Registration / profile logic (mostly unchanged) ----------

@router.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(STRINGS["start_welcome"], reply_markup=start_keyboard())

@router.message(lambda m: m.text == STRINGS["begin_registration"])
async def begin_registration(msg: types.Message, state: FSMContext):
    await state.set_state(RegStates.COURSE)
    await msg.answer(STRINGS["ask_course"])

@router.message(RegStates.COURSE)
async def handle_course(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS.get("cancel_button", "/cancel"):
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    course = validate_course(msg.text)
    if course is None:
        await msg.answer(STRINGS["invalid_course"])
        return
    await state.update_data(course=course)
    await state.set_state(RegStates.DIRECTION)
    await msg.answer(STRINGS["ask_direction"])

@router.message(RegStates.DIRECTION)
async def handle_direction(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS.get("cancel_button", "/cancel"):
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    direction = msg.text.strip()
    if len(direction) < 2 or len(direction) > 120:
        await msg.answer("Неправильное название направления. Попробуйте короче.")
        return
    await state.update_data(direction=direction)
    await state.set_state(RegStates.AGE)
    await msg.answer(STRINGS["ask_age"])

@router.message(RegStates.AGE)
async def handle_age(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS.get("cancel_button", "/cancel"):
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    age = validate_age(msg.text)
    if age is None:
        await msg.answer(STRINGS["invalid_age"])
        return
    await state.update_data(age=age)
    await state.set_state(RegStates.NAME)
    await msg.answer(STRINGS["ask_name"])

@router.message(RegStates.NAME)
async def handle_name(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS.get("cancel_button", "/cancel"):
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    name = validate_name(msg.text)
    if name is None:
        await msg.answer(STRINGS["invalid_name"])
        return
    await state.update_data(name=name)
    await state.set_state(RegStates.DESCRIPTION)
    await msg.answer(STRINGS["ask_description"])

@router.message(RegStates.DESCRIPTION)
async def handle_description(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS.get("cancel_button", "/cancel"):
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    desc = validate_description(msg.text)
    if desc is None:
        await msg.answer(STRINGS["invalid_description"])
        return
    await state.update_data(description=desc)
    await state.set_state(RegStates.PHOTO)
    await msg.answer(STRINGS["ask_photo"], reply_markup=skip_photo_keyboard())

@router.message(RegStates.PHOTO, F.photo)
async def handle_photo(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    prev = data.get("tmp_profile_photo")
    if prev:
        try:
            os.remove(prev)
        except Exception:
            pass
    file = await msg.photo[-1].download()
    with open(file.name, "rb") as f:
        b = f.read()
    saved = save_profile_photo(b)
    await state.update_data(tmp_profile_photo=saved)
    await finalize_registration(msg.from_user, state, msg)

@router.message(RegStates.PHOTO)
async def handle_photo_text(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS["skip_photo"]:
        await finalize_registration(msg.from_user, state, msg)
        return
    await msg.answer("Пожалуйста, загрузите фото или нажмите кнопку пропуска.")

async def finalize_registration(user, state: FSMContext, msg):
    data = await state.get_data()
    course = data.get("course")
    direction = data.get("direction")
    age = data.get("age")
    name = data.get("name")
    description = data.get("description")
    tmp_photo = data.get("tmp_profile_photo")
    existing = get_user(user.id)
    prev_photo = existing.get("profile_photo") if existing else None
    profile_photo_path = tmp_photo if tmp_photo else prev_photo
    create_or_update_user(user.id, getattr(user, "username", None), course=course,
                          direction=direction, age=age, name=name,
                          description=description, profile_photo=profile_photo_path)
    await state.clear()
    if tmp_photo and prev_photo and prev_photo != tmp_photo:
        try:
            os.remove(prev_photo)
        except Exception:
            pass
    await send_profile_preview(user.id, msg.chat.id)

async def send_profile_preview(user_id:int, chat_id:int):
    user = get_user(user_id)
    if not user:
        return
    text = f"{STRINGS['profile_preview_title']}\n\n"
    text += f"Имя: {user.get('name')}\nКурс: {user.get('course')}\nНаправление: {user.get('direction')}\nВозраст: {user.get('age')}\nОписание: {user.get('description')}\n"
    verified_text = STRINGS["verify_pending"] if user.get("verified")==1 else (STRINGS["verify_approved"] if user.get("verified")==2 else (STRINGS["verify_denied"] if user.get("verified")==3 else STRINGS["menu_verify_profile"]))
    kb = main_profile_keyboard(user.get("verified", 0))
    if user.get("profile_photo"):
        try:
            with open(user["profile_photo"], "rb") as f:
                await bot.send_photo(chat_id, f, caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=kb)

# ----------------- View/Edit/Profile menu flows -----------------

@router.message(lambda m: m.text == STRINGS["menu_view_profile"])
async def view_profile(msg: types.Message):
    await send_profile_preview(msg.from_user.id, msg.chat.id)

@router.message(lambda m: m.text == STRINGS["menu_edit_profile"])
async def edit_profile_menu(msg: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Курс"))
    kb.add(types.KeyboardButton("Направление"))
    kb.add(types.KeyboardButton("Возраст"))
    kb.add(types.KeyboardButton("Имя"))
    kb.add(types.KeyboardButton("Описание"))
    kb.add(types.KeyboardButton("Фото"))
    kb.add(types.KeyboardButton(STRINGS["cancel_button"]))
    await msg.answer(STRINGS["edit_menu_prompt"], reply_markup=kb)
    await state.set_state("EDIT_SELECT")

@router.message(F.text, state="EDIT_SELECT")
async def handle_edit_select(msg: types.Message, state: FSMContext):
    text = msg.text
    if text == STRINGS["cancel_button"]:
        await state.clear()
        await msg.answer(STRINGS["registration_cancelled"], reply_markup=start_keyboard())
        return
    mapping = {
        "Курс": "course",
        "Направление": "direction",
        "Возраст": "age",
        "Имя": "name",
        "Описание": "description",
        "Фото": "photo"
    }
    if text not in mapping:
        await msg.answer("Неизвестная опция.")
        return
    key = mapping[text]
    await state.update_data(edit_key=key)
    if key == "course":
        await state.set_state("EDIT_COURSE")
        await msg.answer(STRINGS["ask_course"])
    elif key == "direction":
        await state.set_state("EDIT_DIRECTION")
        await msg.answer(STRINGS["ask_direction"])
    elif key == "age":
        await state.set_state("EDIT_AGE")
        await msg.answer(STRINGS["ask_age"])
    elif key == "name":
        await state.set_state("EDIT_NAME")
        await msg.answer(STRINGS["ask_name"])
    elif key == "description":
        await state.set_state("EDIT_DESCRIPTION")
        await msg.answer(STRINGS["ask_description"])
    elif key == "photo":
        await state.set_state("EDIT_PHOTO")
        await msg.answer(STRINGS["ask_photo"], reply_markup=skip_photo_keyboard())

# handlers for edits (string state names used directly)
@router.message("EDIT_COURSE")
async def edit_course(msg: types.Message, state: FSMContext):
    course = validate_course(msg.text)
    if course is None:
        await msg.answer(STRINGS["invalid_course"])
        return
    user = get_user(msg.from_user.id)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=course,
                          direction=user.get("direction"), age=user.get("age"), name=user.get("name"),
                          description=user.get("description"), profile_photo=user.get("profile_photo"))
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_DIRECTION")
async def edit_direction(msg: types.Message, state: FSMContext):
    direction = msg.text.strip()
    if len(direction) < 2:
        await msg.answer("Неверное направление.")
        return
    user = get_user(msg.from_user.id)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=user.get("course"),
                          direction=direction, age=user.get("age"), name=user.get("name"),
                          description=user.get("description"), profile_photo=user.get("profile_photo"))
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_AGE")
async def edit_age(msg: types.Message, state: FSMContext):
    age = validate_age(msg.text)
    if age is None:
        await msg.answer(STRINGS["invalid_age"])
        return
    user = get_user(msg.from_user.id)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=user.get("course"),
                          direction=user.get("direction"), age=age, name=user.get("name"),
                          description=user.get("description"), profile_photo=user.get("profile_photo"))
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_NAME")
async def edit_name(msg: types.Message, state: FSMContext):
    name = validate_name(msg.text)
    if name is None:
        await msg.answer(STRINGS["invalid_name"])
        return
    user = get_user(msg.from_user.id)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=user.get("course"),
                          direction=user.get("direction"), age=user.get("age"), name=name,
                          description=user.get("description"), profile_photo=user.get("profile_photo"))
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_DESCRIPTION")
async def edit_description(msg: types.Message, state: FSMContext):
    desc = validate_description(msg.text)
    if desc is None:
        await msg.answer(STRINGS["invalid_description"])
        return
    user = get_user(msg.from_user.id)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=user.get("course"),
                          direction=user.get("direction"), age=user.get("age"), name=user.get("name"),
                          description=desc, profile_photo=user.get("profile_photo"))
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_PHOTO", F.photo)
async def edit_photo(msg: types.Message, state: FSMContext):
    user = get_user(msg.from_user.id)
    prev = user.get("profile_photo")
    file = await msg.photo[-1].download()
    with open(file.name, "rb") as f:
        b = f.read()
    saved = save_profile_photo(b)
    create_or_update_user(msg.from_user.id, getattr(msg.from_user, "username", None), course=user.get("course"),
                          direction=user.get("direction"), age=user.get("age"), name=user.get("name"),
                          description=user.get("description"), profile_photo=saved)
    if prev and prev != saved:
        try:
            os.remove(prev)
        except Exception:
            pass
    await state.clear()
    await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(user.get("verified", 0)))

@router.message("EDIT_PHOTO")
async def edit_photo_text(msg: types.Message, state: FSMContext):
    if msg.text == STRINGS["skip_photo"]:
        await state.clear()
        await msg.answer(STRINGS["saved_changes"], reply_markup=main_profile_keyboard(get_user(msg.from_user.id).get("verified", 0)))
    else:
        await msg.answer("Пожалуйста, загрузите фото или нажмите кнопку пропуска.")

# ---------------- Verification process triggers ----------------

@router.message(lambda m: m.text in (STRINGS["menu_verify_profile"], STRINGS["verify_denied"]))
async def begin_verification(msg: types.Message, state: FSMContext):
    await state.set_state(RegStates.ID_UPLOAD)
    await msg.answer(STRINGS["ask_id_photo"])

@router.message(RegStates.ID_UPLOAD, F.photo)
async def handle_id_photo(msg: types.Message, state: FSMContext):
    # save id photo locally (temporary)
    file = await msg.photo[-1].download()
    with open(file.name, "rb") as f:
        b = f.read()
    saved = save_id_photo(b)
    save_id_upload(msg.from_user.id, saved)
    set_verification_status(msg.from_user.id, 1)  # pending
    await msg.answer(STRINGS["verification_sent_admin"])
    from config import ADMIN_CHAT_ID, STRINGS as S
    from keyboards import admin_verification_buttons
    user = get_user(msg.from_user.id)
    caption = f"{S['admin_new_verification']}\n\nИмя: {user['name']}\nКурс: {user['course']}\nНаправление: {user['direction']}\nВозраст: {user['age']}\nОписание: {user['description']}"
    kb = admin_verification_buttons(msg.from_user.id)
    try:
        with open(saved, "rb") as f:
            await bot.send_photo(ADMIN_CHAT_ID, f, caption=caption, reply_markup=kb)
    except Exception:
        await bot.send_message(ADMIN_CHAT_ID, caption, reply_markup=kb)
    await state.clear()

# ------------- Events selection UI + callbacks ---------------

@router.message(lambda m: m.text == STRINGS["menu_choose_events"])
async def choose_events(msg: types.Message):
    # show inline keyboard with events and user's selection highlighted
    all_events = list_events()
    selected = get_user_events(msg.from_user.id)
    kb = events_keyboard(all_events, selected)
    await msg.answer("Выберите события, которые вам интересны (нажмите, чтобы выбрать/снять):", reply_markup=kb)

@router.callback_query(lambda c: (c.data or "").startswith("toggle_event|"))
async def toggle_event_callback(cq: types.CallbackQuery):
    data = cq.data
    parts = data.split("|", 1)
    if len(parts) < 2:
        await cq.answer("Ошибка данных")
        return
    event_name = parts[1]
    uid = cq.from_user.id
    selected = set(get_user_events(uid))
    if event_name in selected:
        # remove
        from db import get_conn
        # we remove via direct DB call (we didn't expose remove single user_event earlier)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_events WHERE user_id = ? AND event_name = ?", (uid, event_name))
        conn.commit()
        conn.close()
        selected.remove(event_name)
    else:
        set_user_event(uid, event_name)
        selected.add(event_name)
    # refresh keyboard
    all_events = list_events()
    kb = events_keyboard(all_events, list(selected))
    await cq.message.edit_reply_markup(kb)
    await cq.answer("Обновлено")

@router.callback_query(lambda c: (c.data or "") == "events_done")
async def events_done_callback(cq: types.CallbackQuery):
    await cq.answer("Сохранено")
    await cq.message.delete_reply_markup()
    # send a confirmation and the main menu
    await bot.send_message(cq.from_user.id, "События сохранены.", reply_markup=main_profile_keyboard(get_user(cq.from_user.id).get("verified", 0)))

# --------------- Search & matching flow -----------------

def score_match(current_user: Dict[str, Any], other_user: Dict[str, Any]) -> float:
    """
    Simple scoring:
      - +5 for each shared event (primary filter)
      - +2 for each shared token in direction (split by spaces)
      - -0.5 * |age difference|
    You can tune the weights here.
    """
    score = 0.0
    try:
        my_events = set(get_user_events(current_user["id"]))
        their_events = set(get_user_events(other_user["id"]))
    except Exception:
        my_events = set()
        their_events = set()
    shared_events = my_events.intersection(their_events)
    score += 5.0 * len(shared_events)

    # direction token overlap
    def tokens(s):
        if not s:
            return set()
        # simple tokens: lowercase words, strip punctuation
        return set(re.findall(r"\w+", s.lower()))
    shared_dirs = tokens(current_user.get("direction", "")) & tokens(other_user.get("direction", ""))
    score += 2.0 * len(shared_dirs)

    # age difference penalty
    if current_user.get("age") and other_user.get("age"):
        score -= 0.5 * abs(current_user["age"] - other_user["age"])

    # tiny tie-breaker by user id
    score += (other_user["id"] % 1000) * 1e-6
    return score

def build_search_session(user_id: int) -> None:
    """
    Build & store search session for user_id. Filters:
      - only verified users (verified == 2)
      - exclude self
      - ranking by score_match
    """
    pool = get_verified_pool(user_id)
    me = get_user(user_id)
    if not me:
        session = {"list": [], "index": 0, "seen_ids": set(), "excluded": set()}
        search_sessions[user_id] = session
        return
    # compute scores
    scored = []
    for other in pool:
        # optionally skip if missing fields, but we'll include all
        s = score_match(me, other)
        scored.append((s, other))
    # sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    ranked = [other for s, other in scored]
    session = {"list": ranked, "index": 0, "seen_ids": set(), "excluded": set()}
    search_sessions[user_id] = session

async def send_search_profile(user_id:int, chat_id:int):
    """
    Sends current profile in the user's search session (by index).
    """
    session = search_sessions.get(user_id)
    if not session or not session["list"]:
        await bot.send_message(chat_id, STRINGS["no_profiles"])
        return
    idx = session["index"]
    if idx < 0:
        idx = 0
        session["index"] = 0
    if idx >= len(session["list"]):
        idx = len(session["list"]) - 1
        session["index"] = idx
    profile = session["list"][idx]
    # Build text
    text = f"Имя: {profile.get('name')}\nКурс: {profile.get('course')}\nНаправление: {profile.get('direction')}\nВозраст: {profile.get('age')}\nОписание: {profile.get('description')}\n@{profile.get('username') or 'нет_юзернейма'}"
    kb = search_inline_keyboard()
    if profile.get("profile_photo"):
        try:
            with open(profile["profile_photo"], "rb") as f:
                await bot.send_photo(chat_id, f, caption=text, reply_markup=kb)
            return
        except Exception:
            pass
    await bot.send_message(chat_id, text, reply_markup=kb)

@router.message(lambda m: m.text == STRINGS["search_begin"])
async def start_search(msg: types.Message):
    # only for verified users
    user = get_user(msg.from_user.id)
    if not user or user.get("verified") != 2:
        await msg.answer("Доступно только верифицированным пользователям.")
        return
    build_search_session(msg.from_user.id)
    # if empty
    session = search_sessions.get(msg.from_user.id)
    if not session or not session["list"]:
        await msg.answer(STRINGS["no_profiles"])
        return
    # send first profile
    await send_search_profile(msg.from_user.id, msg.chat.id)

# Callback handlers: prev, next, like, dislike
@router.callback_query(lambda c: c.data in ("search_next", "search_prev", "search_like", "search_dislike"))
async def search_callbacks(cq: types.CallbackQuery):
    uid = cq.from_user.id
    session = search_sessions.get(uid)
    if not session:
        # rebuild session if missing
        build_search_session(uid)
        session = search_sessions.get(uid)
        if not session or not session["list"]:
            await cq.answer(STRINGS["no_profiles"], show_alert=True)
            return
    data = cq.data
    if data == "search_next":
        if session["index"] < len(session["list"]) - 1:
            session["index"] += 1
            await cq.message.delete()  # remove previous to keep chat clean
            await send_search_profile(uid, cq.message.chat.id)
        else:
            await cq.answer("Это последний профиль.")
    elif data == "search_prev":
        if session["index"] > 0:
            session["index"] -= 1
            await cq.message.delete()
            await send_search_profile(uid, cq.message.chat.id)
        else:
            await cq.answer("Это первый профиль.")
    elif data == "search_like":
        # like current profile
        current = session["list"][session["index"]]
        target_id = current["id"]
        db_like_user(uid, target_id)
        # check mutual
        if is_mutual(uid, target_id):
            # notify both
            their = get_user(target_id)
            me = get_user(uid)
            # send usernames if exist
            my_handle = f"@{me.get('username')}" if me.get("username") else f"user_{me.get('id')}"
            their_handle = f"@{their.get('username')}" if their.get("username") else f"user_{their.get('id')}"
            try:
                await bot.send_message(uid, STRINGS["match_notify"].replace("{other_username}", their_handle).replace("@{other_username}", their_handle))
            except Exception:
                pass
            try:
                await bot.send_message(target_id, STRINGS["match_notify"].replace("{other_username}", my_handle).replace("@{other_username}", my_handle))
            except Exception:
                pass
        # remove this profile from the session's list (hide)
        session["excluded"].add(target_id)
        session["list"].pop(session["index"])
        # adjust index
        if session["index"] >= len(session["list"]):
            session["index"] = max(0, len(session["list"]) - 1)
        # refresh: delete previous message and send new current or say no more
        await cq.message.delete()
        if session["list"]:
            await send_search_profile(uid, cq.message.chat.id)
        else:
            await bot.send_message(uid, "Профилей больше нет.")
    elif data == "search_dislike":
        # hide current profile without liking
        current = session["list"][session["index"]]
        target_id = current["id"]
        session["excluded"].add(target_id)
        session["list"].pop(session["index"])
        if session["index"] >= len(session["list"]):
            session["index"] = max(0, len(session["list"]) - 1)
        await cq.message.delete()
        if session["list"]:
            await send_search_profile(uid, cq.message.chat.id)
        else:
            await bot.send_message(uid, "Профилей больше нет.")
    await cq.answer()
