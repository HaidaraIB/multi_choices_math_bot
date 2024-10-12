from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from common.keyboards import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button
import models


def build_broadcast_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="الجميع 👥",
                callback_data="all users",
            ),
            InlineKeyboardButton(
                text="مستخدمين محددين 👤",
                callback_data="specific users",
            ),
        ],
        build_back_button("back to the message"),
        back_to_admin_home_page_button[0],
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_to(users: list[models.User], context: ContextTypes.DEFAULT_TYPE):
    msg: Message = context.user_data["the message"]
    media_types = {
        "photo": msg.photo[-1] if msg.photo else None,
        "video": msg.video,
        "audio": msg.audio,
        "voice": msg.voice,
    }
    for m_type, m in media_types.items():
        if m:
            media = m
            media_type = m_type
            break

    for user in users:
        chat_id = user.id if isinstance(user, models.User) else user
        try:
            if media:
                send_func = getattr(context.bot, f"send_{media_type}")
                await send_func(
                    chat_id=chat_id,
                    caption=msg.caption,
                    **{media_type: media},
                )
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg.text)
        except:
            continue


def build_done_button():
    done_button = [
        [
            InlineKeyboardButton(
                text="تم الانتهاء 👍",
                callback_data="done entering users",
            )
        ],
        build_back_button("back_to_send_to"),
        back_to_admin_home_page_button[0],
    ]
    return InlineKeyboardMarkup(done_button)
