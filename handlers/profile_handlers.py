from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import database as db
import strings
import keyboards as kb
import utils
from states import EditProfileStates, EventSelectionStates

router = Router()


@router.message(F.text == strings.BTN_VIEW_PROFILE)
async def view_profile(message: Message):
    """View user profile"""
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer("Профиль не найден. Используйте /start")
        return
    
    profile_text = utils.format_profile(user)
    await utils.send_profile_with_photo(message, user, profile_text)


@router.message(F.text == strings.BTN_EDIT_PROFILE)
async def edit_profile(message: Message, state: FSMContext):
    """Start editing profile"""
    await message.answer(
        strings.EDIT_PROFILE_CHOOSE,
        reply_markup=kb.get_edit_profile_keyboard()
    )
    await state.set_state(EditProfileStates.choosing_field)


@router.message(EditProfileStates.choosing_field, F.text == "Курс")
async def edit_course(message: Message, state: FSMContext):
    """Edit course"""
    await message.answer(
        strings.REG_COURSE_QUESTION,
        reply_markup=kb.get_course_keyboard()
    )
    await state.set_state(EditProfileStates.editing_course)


@router.message(EditProfileStates.editing_course)
async def process_edit_course(message: Message, state: FSMContext):
    """Process course edit"""
    if message.text == strings.BTN_CANCEL:
        await cancel_edit(message, state)
        return
    
    if message.text not in strings.COURSES:
        await message.answer(strings.ERROR_INVALID_INPUT)
        return
    
    db.update_user_field(message.from_user.id, 'course', message.text)
    await finish_edit(message, state)


@router.message(EditProfileStates.choosing_field, F.text == "Направление")
async def edit_program(message: Message, state: FSMContext):
    """Edit program"""
    await message.answer(
        strings.REG_PROGRAM_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(EditProfileStates.editing_program)


@router.message(EditProfileStates.editing_program)
async def process_edit_program(message: Message, state: FSMContext):
    """Process program edit"""
    if message.text == strings.BTN_CANCEL:
        await cancel_edit(message, state)
        return
    
    db.update_user_field(message.from_user.id, 'program', message.text)
    await finish_edit(message, state)


@router.message(EditProfileStates.choosing_field, F.text == "Возраст")
async def edit_age(message: Message, state: FSMContext):
    """Edit age"""
    await message.answer(
        strings.REG_AGE_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(EditProfileStates.editing_age)


@router.message(EditProfileStates.editing_age)
async def process_edit_age(message: Message, state: FSMContext):
    """Process age edit"""
    if message.text == strings.BTN_CANCEL:
        await cancel_edit(message, state)
        return
    
    age = utils.validate_age(message.text)
    if age is None:
        await message.answer(strings.ERROR_INVALID_AGE)
        return
    
    db.update_user_field(message.from_user.id, 'age', age)
    await finish_edit(message, state)


@router.message(EditProfileStates.choosing_field, F.text == "Имя")
async def edit_name(message: Message, state: FSMContext):
    """Edit name"""
    await message.answer(
        strings.REG_NAME_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(EditProfileStates.editing_name)


@router.message(EditProfileStates.editing_name)
async def process_edit_name(message: Message, state: FSMContext):
    """Process name edit"""
    if message.text == strings.BTN_CANCEL:
        await cancel_edit(message, state)
        return
    
    db.update_user_field(message.from_user.id, 'name', message.text)
    await finish_edit(message, state)


@router.message(EditProfileStates.choosing_field, F.text == "Описание")
async def edit_description(message: Message, state: FSMContext):
    """Edit description"""
    await message.answer(
        strings.REG_DESCRIPTION_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(EditProfileStates.editing_description)


@router.message(EditProfileStates.editing_description)
async def process_edit_description(message: Message, state: FSMContext):
    """Process description edit"""
    if message.text == strings.BTN_CANCEL:
        await cancel_edit(message, state)
        return
    
    if not utils.validate_description(message.text):
        await message.answer(strings.ERROR_INVALID_DESCRIPTION)
        return
    
    db.update_user_field(message.from_user.id, 'description', message.text)
    await finish_edit(message, state)


@router.message(EditProfileStates.choosing_field, F.text == "Фото")
async def edit_photo(message: Message, state: FSMContext):
    """Edit photo"""
    await message.answer(
        strings.REG_PHOTO_QUESTION,
        reply_markup=kb.get_skip_photo_keyboard()
    )
    await state.set_state(EditProfileStates.editing_photo)


@router.message(EditProfileStates.editing_photo, F.text == strings.BTN_SKIP_PHOTO)
async def remove_photo(message: Message, state: FSMContext):
    """Remove photo"""
    user = db.get_user(message.from_user.id)
    if user and user['photo_id']:
        utils.delete_photo(message.from_user.id, 'profile')
    
    db.update_user_field(message.from_user.id, 'photo_id', None)
    await finish_edit(message, state)


@router.message(EditProfileStates.editing_photo, F.photo)
async def process_edit_photo(message: Message, state: FSMContext):
    """Process photo edit"""
    # Delete old photo
    user = db.get_user(message.from_user.id)
    if user and user['photo_id']:
        utils.delete_photo(message.from_user.id, 'profile')
    
    # Save new photo
    photo_id = await utils.download_photo(message, message.from_user.id, 'profile')
    db.update_user_field(message.from_user.id, 'photo_id', photo_id)
    await finish_edit(message, state)


@router.message(EditProfileStates.editing_photo)
async def invalid_photo_edit(message: Message):
    """Handle invalid photo input during edit"""
    await message.answer(
        strings.ERROR_INVALID_PHOTO,
        reply_markup=kb.get_skip_photo_keyboard()
    )


@router.message(F.text == strings.BTN_CHOOSE_EVENTS)
async def choose_events(message: Message, state: FSMContext):
    """Start choosing events"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    await message.answer(
        strings.EVENTS_CHOOSE,
        reply_markup=kb.get_events_keyboard(user['events'])
    )
    await state.set_state(EventSelectionStates.selecting_events)
    await state.update_data(selected_events=user['events'])


@router.callback_query(EventSelectionStates.selecting_events, F.data.startswith("event_"))
async def toggle_event(callback: CallbackQuery, state: FSMContext):
    """Toggle event selection"""
    event_name = callback.data.split("event_", 1)[1]
    data = await state.get_data()
    selected = data.get('selected_events', [])
    
    if event_name in selected:
        selected.remove(event_name)
    else:
        selected.append(event_name)
    
    await state.update_data(selected_events=selected)
    await callback.message.edit_reply_markup(
        reply_markup=kb.get_events_keyboard(selected)
    )
    await callback.answer()


@router.callback_query(EventSelectionStates.selecting_events, F.data == "events_save")
async def save_events(callback: CallbackQuery, state: FSMContext):
    """Save selected events"""
    data = await state.get_data()
    selected = data.get('selected_events', [])
    
    db.update_user_events(callback.from_user.id, selected)
    
    user = db.get_user(callback.from_user.id)
    await callback.message.edit_text(strings.EVENTS_SELECTED)
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )
    await state.clear()
    await callback.answer()


async def finish_edit(message: Message, state: FSMContext):
    """Finish editing and show profile"""
    user = db.get_user(message.from_user.id)
    await message.answer(
        strings.EDIT_COMPLETE,
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )
    await state.clear()


async def cancel_edit(message: Message, state: FSMContext):
    """Cancel editing"""
    user = db.get_user(message.from_user.id)
    await state.clear()
    await message.answer(
        strings.CANCEL_MESSAGE,
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )