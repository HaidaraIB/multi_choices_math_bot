from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
from common.keyboards import build_back_button, build_admin_keyboard
from common.constants import *
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from admin.questions_settings.q_settings import back_to_q_settings_handler
from start import admin_command
import models

CAT_NAME = 0


async def add_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_q_settings"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل اسم المجموعة الجديدة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CAT_NAME


async def get_cat_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await models.Category.add(name=update.message.text)
        await update.message.reply_text(
            text="تمت إضافة المجموعة بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_cat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_cat,
            "^add_cat$",
        )
    ],
    states={
        CAT_NAME: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_cat_name,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
    ],
)
