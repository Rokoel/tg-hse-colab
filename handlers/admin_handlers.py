from aiogram import Router, F
from aiogram.types import CallbackQuery
import database as db
import strings
import utils
import config
from handlers import user_handlers

router = Router()


def is_admin_chat(chat_id: int) -> bool:
    """Check if message is from admin chat"""
    return chat_id == config.ADMIN_CHAT_ID


@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_verification(callback: CallbackQuery):
    """Approve user verification"""
    # Check if in admin chat
    if not is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта команда доступна только в админ-чате!", show_alert=True)
        return
    
    user_id = int(callback.data.split("admin_approve_")[1])
    user = db.get_user(user_id)
    
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return
    
    # Update verification status
    db.set_verification_status(user_id, 'verified')
    
    # Delete student ID photo as it's no longer needed
    if user['student_id_photo']:
        utils.delete_photo(user_id, 'student_id')
        db.remove_student_id_photo(user_id)
    
    # Update admin message
    admin_name = callback.from_user.first_name or "Admin"
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        strings.ADMIN_VERIFICATION_APPROVED.format(admin_name=admin_name)
    )
    
    # Notify user
    try:
        user_updated = db.get_user(user_id)
        await callback.bot.send_message(
            chat_id=user_id,
            text=strings.VERIFY_APPROVED
        )
        
        # Send updated menu
        from keyboards import get_main_menu_keyboard
        await callback.bot.send_message(
            chat_id=user_id,
            text="Выбери действие:",
            reply_markup=get_main_menu_keyboard(user_updated['verification_status'])
        )
    except Exception:
        pass  # User might have blocked the bot
    
    await callback.answer("Верификация подтверждена!")


@router.callback_query(F.data.startswith("admin_deny_"))
async def deny_verification(callback: CallbackQuery):
    """Deny user verification"""
    # Check if in admin chat
    if not is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта команда доступна только в админ-чате!", show_alert=True)
        return
    
    user_id = int(callback.data.split("admin_deny_")[1])
    user = db.get_user(user_id)
    
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return
    
    # Update verification status
    db.set_verification_status(user_id, 'denied')
    
    # Delete student ID photo
    if user['student_id_photo']:
        utils.delete_photo(user_id, 'student_id')
        db.remove_student_id_photo(user_id)
    
    # Update admin message
    admin_name = callback.from_user.first_name or "Admin"
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        strings.ADMIN_VERIFICATION_DENIED.format(admin_name=admin_name)
    )
    
    # Notify user
    try:
        user_updated = db.get_user(user_id)
        await callback.bot.send_message(
            chat_id=user_id,
            text=strings.VERIFY_DENIED
        )
        
        # Send updated menu
        from keyboards import get_main_menu_keyboard
        await callback.bot.send_message(
            chat_id=user_id,
            text="Выбери действие:",
            reply_markup=get_main_menu_keyboard(user_updated['verification_status'])
        )
    except Exception:
        pass  # User might have blocked the bot
    
    await callback.answer("Верификация отклонена!")


@router.callback_query(F.data.startswith("admin_ban_report_"))
async def ban_reported_user(callback: CallbackQuery):
    """Ban reported user"""
    # Check if in admin chat
    if not is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта команда доступна только в админ-чате!", show_alert=True)
        return
    
    reported_user_id = int(callback.data.split("admin_ban_report_")[1].split("_")[0])
    reporter_user_id = int(callback.data.split("admin_ban_report_")[1].split("_")[1])
    user = db.get_user(reported_user_id)
    
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return
    
    # Ban user
    db.ban_user(reported_user_id)
    
    # Delete all photos
    if user['photo_id']:
        utils.delete_photo(reported_user_id, 'profile')
    if user['student_id_photo']:
        utils.delete_photo(reported_user_id, 'student_id')
        db.remove_student_id_photo(reported_user_id)
    
    # Update admin message
    admin_name = callback.from_user.first_name or "Admin"
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        strings.ADMIN_REPORT_USER_BANNED.format(admin_name=admin_name)
    )
    
    # Notify users
    try:
        await callback.bot.send_message(
            chat_id=reported_user_id,
            text="🚫 Вы были заблокированы администрацией."
        )
    except Exception:
        print("Caught exception while banning user")
        pass  # User might have blocked the bot

    try:
        await callback.bot.send_message(
            chat_id=reporter_user_id,
            text="Ваша жалоба привела к блокировке пользователя, благодарим за помощь!"
        )
    except Exception:
        pass  # User might have blocked the bot
    
    await callback.answer("Пользователь заблокирован!")


@router.callback_query(F.data.startswith("admin_ban_"))
async def ban_user(callback: CallbackQuery):
    """Ban user from using the bot"""
    # Check if in admin chat
    if not is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта команда доступна только в админ-чате!", show_alert=True)
        return
    
    if (callback.data.startswith("admin_ban_report_")):
        return
    user_id = int(callback.data.split("admin_ban_")[1])
    user = db.get_user(user_id)
    
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return
    
    # Ban user
    db.ban_user(user_id)
    
    # Delete all photos
    if user['photo_id']:
        utils.delete_photo(user_id, 'profile')
    if user['student_id_photo']:
        utils.delete_photo(user_id, 'student_id')
        db.remove_student_id_photo(user_id)
    
    # Update admin message
    admin_name = callback.from_user.first_name or "Admin"
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        strings.ADMIN_USER_BANNED.format(admin_name=admin_name)
    )
    
    # Notify user
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="🚫 Вы были заблокированы администрацией."
        )
    except Exception:
        pass  # User might have blocked the bot
    
    await callback.answer("Пользователь заблокирован!")


@router.callback_query(F.data.startswith("admin_dismiss_report_"))
async def dismiss_report(callback: CallbackQuery):
    """Dismiss user report"""
    # Check if in admin chat
    if not is_admin_chat(callback.message.chat.id):
        await callback.answer("Эта команда доступна только в админ-чате!", show_alert=True)
        return
    
    user_id = int(callback.data.split("admin_dismiss_report_")[1])
    
    # Update admin message
    admin_name = callback.from_user.first_name or "Admin"
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        strings.ADMIN_REPORT_DISMISSED.format(admin_name=admin_name)
    )
    
    await callback.answer("Жалоба отклонена!")