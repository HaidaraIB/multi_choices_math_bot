from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from common.back_to_home_page import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from common.keyboards import build_user_keyboard, build_back_button
import models
from start import start_command
from user.user_calls.common import build_user_settings_keyboard

PHONE = 0


async def user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        keyboard = build_user_settings_keyboard()
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر ماذا تريد أن تفعل",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


async def update_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        back_buttons = [
            build_back_button("back_to_update_phone_number"),
            back_to_user_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل رقم الهاتف مسبوقاً بنداء الدولة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return PHONE


back_to_update_phone_number = user_settings


async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        phone = update.message.text
        await models.User.update(
            user_id=update.effective_user.id,
            field="phone_number",
            value=phone,
        )
        await update.message.reply_text(
            text="تم تحديث رقم الهاتف بنجاح ✅",
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


user_settings_handler = CallbackQueryHandler(user_settings, "^user_settings$")
back_to_update_phone_number_handler = CallbackQueryHandler(
    back_to_update_phone_number, "^back_to_update_phone_number$"
)

update_phone_number_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            update_phone_number,
            "^update_phone_number$",
        )
    ],
    states={
        PHONE: [
            MessageHandler(
                filters=filters.Regex("^\+?\d+$"),
                callback=get_phone_number,
            )
        ]
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        back_to_update_phone_number_handler,
    ],
)
