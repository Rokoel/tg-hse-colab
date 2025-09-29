
from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_CHAT_ID, STRINGS
from db import set_verification_status, pop_id_upload, get_user, ban_user, is_banned, add_event, remove_event, list_events, ensure_events
from keyboards import admin_verification_buttons
import os

router = Router()

# Only allow admin group id - simple check
def is_admin_chat(chat_id: int) -> bool:
    return chat_id == ADMIN_CHAT_ID

@router.callback_query()
async def admin_callbacks(cq: types.CallbackQuery):
    # we expect callback_data like: "admin_verify|approve|<user_id>"
    data = cq.data or ""
    if not data.startswith("admin_verify|"):
        return
    parts = data.split("|")
    if len(parts) < 3:
        await cq.answer("Invalid.")
        return
    action = parts[1]
    user_id = int(parts[2])
    if not is_admin_chat(cq.message.chat.id):
        await cq.answer("Эта команда доступна только в админ-чате.", show_alert=True)
        return
    if action == "approve":
        set_verification_status(user_id, 2)
        # delete stored id image if present
        path = pop_id_upload(user_id)
        if path:
            try:
                os.remove(path)
            except Exception:
                pass
        await cq.message.edit_reply_markup(None)  # remove buttons
        await cq.message.reply(f"Пользователь {user_id} подтверждён.")
        # notify user
        await cq.bot.send_message(user_id, STRINGS["verification_approved_notify"])
    elif action == "deny":
        set_verification_status(user_id, 3)
        # keep id photo (or remove? spec: store only until decision -> but we may want to keep for admin review)
        path = pop_id_upload(user_id)  # pop returns and deletes from DB; we may still want to keep file for evidence; spec says remove when not needed -> let's remove
        if path:
            try:
                os.remove(path)
            except Exception:
                pass
        await cq.message.edit_reply_markup(None)
        await cq.message.reply(f"Пользователь {user_id} отклонён.")
        await cq.bot.send_message(user_id, STRINGS["verification_denied_notify"])
    elif action == "ban":
        ban_user(user_id)
        await cq.message.edit_reply_markup(None)
        await cq.message.reply(f"Пользователь {user_id} забанен.")
        try:
            await cq.bot.send_message(user_id, "Вы забанены от использования бота.")
        except Exception:
            pass
    await cq.answer()  # ack

# Admin management of events: simple text commands in admin chat
@router.message(Command("events"))
async def cmd_events(msg: types.Message):
    if not is_admin_chat(msg.chat.id):
        return
    evs = list_events()
    text = "Текущие события:\n" + "\n".join(f"- {e}" for e in evs)
    text += "\n\nДобавить: /addevent <name>\nУдалить: /rmevent <name>"
    await msg.reply(text)

@router.message(Command("addevent"))
async def cmd_addevent(msg: types.Message):
    if not is_admin_chat(msg.chat.id):
        return
    args = msg.get_args()
    if not args:
        await msg.reply("Использование: /addevent <название события>")
        return
    add_event(args.strip())
    await msg.reply(f"Добавлено: {args.strip()}")

@router.message(Command("rmevent"))
async def cmd_rmevent(msg: types.Message):
    if not is_admin_chat(msg.chat.id):
        return
    args = msg.get_args()
    if not args:
        await msg.reply("Использование: /rmevent <название события>")
        return
    remove_event(args.strip())
    await msg.reply(f"Удалено (если было): {args.strip()}")
