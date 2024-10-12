from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import models
from admin.questions_settings.q_settings import back_to_q_settings_handler
from common.keyboards import (
    build_back_button,
    build_confirmation_keyboard,
    build_admin_keyboard,
)
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.constants import *
from admin.questions_settings.common import (
    CATEGORY,
    Q,
    choose_q_option,
    choose_cat,
    back_to_choose_cat,
)
from custom_filters import Admin
from start import admin_command

CONFIRM_DELETE_Q = 2


async def choose_q_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_q_id = int(update.callback_query.data)
            context.user_data["q_to_remove"] = chosen_q_id
        else:
            chosen_q_id = context.user_data["q_to_remove"]

        keyboard = build_confirmation_keyboard(data="remove_q")
        keyboard.append(build_back_button("back_to_choose_q_to_remove"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="هل أنت متأكد من أنك تريد حذف هذا السؤال؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_DELETE_Q


back_to_choose_q_to_remove = choose_cat


async def confirm_delete_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            await models.Question.delete(q_id=context.user_data["q_to_remove"])
            await update.callback_query.answer(
                text="تم حذف السؤال بنجاح ✅",
                show_alert=True,
            )
        else:
            await update.callback_query.answer(
                text="تم الإلغاء ❌",
                show_alert=True,
            )

        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


remove_q_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^remove_q$",
        )
    ],
    states={
        CATEGORY: [
            CallbackQueryHandler(
                choose_cat,
                "^\d+$",
            )
        ],
        Q: [
            CallbackQueryHandler(
                choose_q_to_remove,
                "^\d+$",
            )
        ],
        CONFIRM_DELETE_Q: [
            CallbackQueryHandler(
                confirm_delete_q,
                "^((yes)|(no)) remove_q$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
        CallbackQueryHandler(
            back_to_choose_q_to_remove, "^back_to_choose_q_to_remove$"
        ),
        CallbackQueryHandler(
            back_to_choose_cat, "^back_to_choose_cat$"
        ),
    ],
)
