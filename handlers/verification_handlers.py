from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import database as db
import strings
import keyboards as kb
import utils
from states import VerificationStates, StartStates
import config

router = Router()


@router.message(F.text.in_([strings.BTN_VERIFY_PROFILE, strings.BTN_RETRY_VERIFICATION, strings.BTN_ALREADY_VERIFIED]))
async def start_verification(message: Message, state: FSMContext):
    """Start verification process"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    # Check if already verified
    if user['verification_status'] == 'verified':
        await message.answer(
            strings.USER_ALREADY_VERIFIED,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        return
    
    await message.answer(
        strings.VERIFY_SEND_ID,
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VerificationStates.waiting_for_student_id)


@router.message(F.text == strings.BTN_VERIFICATION_PENDING)
async def check_verification_status(message: Message):
    """Check verification status"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    if user['verification_status'] == 'pending':
        await message.answer(
            strings.VERIFICATION_MESSAGE_PENDING,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )


@router.message(VerificationStates.waiting_for_student_id, F.photo)
async def process_student_id(message: Message, state: FSMContext):
    """Process student ID photo"""
    # Delete old student ID photo if exists
    user = db.get_user(message.from_user.id)
    if user and user['student_id_photo']:
        utils.delete_photo(message.from_user.id, 'student_id')
    
    # Save new student ID photo
    photo_id = await utils.download_photo(message, message.from_user.id, 'student_id')
    db.save_student_id_photo(message.from_user.id, photo_id)
    
    # Set status to pending
    db.set_verification_status(message.from_user.id, 'pending')
    
    # Send to admin chat
    await send_to_admin_chat(message, photo_id)
    
    # Notify user
    user = db.get_user(message.from_user.id)
    await message.answer(
        strings.VERIFY_SUBMITTED,
        reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
    )
    await state.set_state(StartStates.start)


@router.message(VerificationStates.waiting_for_student_id)
async def invalid_student_id(message: Message, state: FSMContext):
    """Handle invalid student ID input"""
    if message.text == strings.BTN_CANCEL:
        user = db.get_user(message.from_user.id)
        await state.set_state(StartStates.start)
        await message.answer(
            strings.CANCEL_MESSAGE,
            reply_markup=kb.get_main_menu_keyboard(user['verification_status'])
        )
        return
    
    await message.answer(
        strings.ERROR_INVALID_PHOTO,
        reply_markup=kb.get_cancel_keyboard()
    )


async def send_to_admin_chat(message: Message, student_id_photo: str):
    """Send verification request to admin chat"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    # Format admin message
    admin_text = strings.ADMIN_NEW_VERIFICATION.format(user_id=message.from_user.id)
    admin_text += "\n\n" + utils.format_profile(user, show_verification=False)
    
    # Send profile photo if exists
    if user['photo_id']:
        try:
            await message.bot.send_photo(
                chat_id=config.ADMIN_CHAT_ID,
                photo=user['photo_id'],
                caption=admin_text
            )
        except Exception:
            await message.bot.send_message(
                chat_id=config.ADMIN_CHAT_ID,
                text=admin_text
            )
    else:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=admin_text
        )
    
    # Send student ID photo
    await message.bot.send_photo(
        chat_id=config.ADMIN_CHAT_ID,
        photo=student_id_photo,
        caption="📸 Фото студенческого билета",
        reply_markup=kb.get_admin_verification_keyboard(message.from_user.id)
    )