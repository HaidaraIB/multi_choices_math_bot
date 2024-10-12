from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
from admin.questions_settings.common import build_q_settings_keyboard
from common.back_to_home_page import back_to_admin_home_page_button


async def q_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_q_settings_keyboard()
        keyboard.append(back_to_admin_home_page_button[0])

        await update.callback_query.edit_message_text(
            text="إعدادات الأسئلة",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


back_to_q_settings = q_settings


q_settings_handler = CallbackQueryHandler(q_settings, "^q settings$")
back_to_q_settings_handler = CallbackQueryHandler(
    back_to_q_settings, "^back_to_q_settings$"
)
