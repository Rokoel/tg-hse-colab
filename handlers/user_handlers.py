from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
import database as db
import strings
import keyboards as kb
import utils
from states import RegistrationStates
import config
import os

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    # Check if user is banned
    if db.user_exists(message.from_user.id) and db.is_user_banned(message.from_user.id):
        await message.answer(strings.USER_BLOCKED_MESSAGE)
        return
    
    # Check if user already registered
    if db.user_exists(message.from_user.id):
        user = db.get_user(message.from_user.id)
        await message.answer(
            strings.USER_ALREADY_REGISTERED,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        return
    
    # Send welcome message with privacy policy
    if os.path.exists(config.PRIVACY_POLICY_PATH):
        policy_file = FSInputFile(config.PRIVACY_POLICY_PATH)
        await message.answer_document(
            document=policy_file,
            caption=strings.WELCOME_MESSAGE,
            reply_markup=kb.get_accept_privacy_keyboard()
        )
    else:
        await message.answer(
            strings.WELCOME_MESSAGE,
            reply_markup=kb.get_accept_privacy_keyboard()
        )

@router.message(F.text == strings.BTN_BEGIN_REGISTRATION)
async def accept_privacy(message: Message, state: FSMContext):
    """User accepted privacy policy, start registration"""
    await message.answer(
        strings.REG_NAME_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_name)

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Process name input"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    await state.update_data(name=message.text)
    await message.answer(
        strings.REG_AGE_QUESTION.format(name=message.text),
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_age)


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Process age input"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    age = utils.validate_age(message.text)
    if age is None:
        await message.answer(
            strings.ERROR_INVALID_AGE,
            reply_markup=kb.get_cancel_keyboard()
        )
        return
    
    await state.update_data(age=age)
    await message.answer(
        strings.REG_DESCRIPTION_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_description)


@router.message(RegistrationStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process description input"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    if not utils.validate_description(message.text):
        await message.answer(
            strings.ERROR_INVALID_DESCRIPTION,
            reply_markup=kb.get_cancel_keyboard()
        )
        return
    
    await state.update_data(description=message.text)
    await message.answer(
        strings.REG_COURSE_QUESTION,
        reply_markup=kb.get_course_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_course)


@router.message(RegistrationStates.waiting_for_course)
async def process_course(message: Message, state: FSMContext):
    """Process course selection"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    if message.text not in strings.COURSES:
        await message.answer(
            strings.ERROR_INVALID_INPUT,
            reply_markup=kb.get_course_keyboard()
        )
        return
    
    await state.update_data(course=message.text)
    await message.answer(
        strings.REG_PROGRAM_QUESTION,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_program)


@router.message(RegistrationStates.waiting_for_program)
async def process_program(message: Message, state: FSMContext):
    """Process program input"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    await state.update_data(program=message.text)
    await message.answer(
        strings.REG_PHOTO_QUESTION,
        reply_markup=kb.get_skip_photo_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_photo)


@router.message(RegistrationStates.waiting_for_photo, F.text == strings.BTN_SKIP_PHOTO)
async def skip_photo(message: Message, state: FSMContext):
    """Skip photo and complete registration"""
    await complete_registration(message, state, None)


@router.message(RegistrationStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Process photo upload"""
    photo_id = await utils.download_photo(message, message.from_user.id, 'profile')
    await complete_registration(message, state, photo_id)


@router.message(RegistrationStates.waiting_for_photo)
async def invalid_photo(message: Message, state: FSMContext):
    """Handle invalid photo input"""
    if message.text == strings.BTN_CANCEL:
        await cancel_registration(message, state)
        return
    
    await message.answer(
        strings.ERROR_INVALID_PHOTO,
        reply_markup=kb.get_skip_photo_keyboard()
    )


async def complete_registration(message: Message, state: FSMContext, photo_id: str):
    """Complete the registration process"""
    data = await state.get_data()
    
    # Create user in database
    db.create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        course=data['course'],
        program=data['program'],
        age=data['age'],
        name=data['name'],
        description=data['description'],
        photo_id=photo_id
    )
    
    user = db.get_user(message.from_user.id)
    profile_text = strings.REG_COMPLETE + utils.format_profile(user)
    
    await utils.send_profile_with_photo(message, user, profile_text)
    await message.answer(
        strings.REG_COMPLETE_CHOOSE_ACTION.format(name=data['name']),
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )
    
    await state.clear()


async def cancel_registration(message: Message, state: FSMContext):
    """Cancel registration"""
    await state.clear()
    await message.answer(
        strings.CANCEL_MESSAGE,
        reply_markup=kb.get_start_keyboard() if not db.user_exists(message.from_user.id) else None
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    
    await state.clear()
    user = db.get_user(message.from_user.id)
    if user:
        await message.answer(
            strings.CANCEL_MESSAGE,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
    else:
        await message.answer(strings.CANCEL_MESSAGE)