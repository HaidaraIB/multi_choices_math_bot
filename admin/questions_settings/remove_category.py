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
from custom_filters import Admin
from admin.questions_settings.common import choose_q_option, CATEGORY

from start import admin_command

CONFIRM_DELETE_CAT = 1


async def choose_cat_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_cat_id = int(update.callback_query.data)
            context.user_data["cat_to_remove"] = chosen_cat_id
        else:
            chosen_cat_id = context.user_data["cat_to_remove"]

        cat = models.Category.get_by(cat_id=chosen_cat_id)
        keyboard = build_confirmation_keyboard(data="remove_cat")
        keyboard.append(build_back_button("back_to_choose_cat_to_remove"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=f"سيتم حذف المجموعة <code>{cat.name}</code> وجميع الأسئلة التابعة لها هل أنت متأكد؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_DELETE_CAT


back_to_choose_cat_to_remove = choose_q_option


async def confirm_delete_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            await models.Category.delete(cat_id=context.user_data["cat_to_remove"])
            await update.callback_query.answer(
                text="تم حذف المجموعة بنجاح ✅",
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


remove_cat_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^remove_cat$",
        )
    ],
    states={
        CATEGORY: [
            CallbackQueryHandler(
                choose_cat_to_remove,
                "^\d+$",
            )
        ],
        CONFIRM_DELETE_CAT: [
            CallbackQueryHandler(
                confirm_delete_cat,
                "^((yes)|(no)) remove_cat$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
        CallbackQueryHandler(
            back_to_choose_cat_to_remove, "^back_to_choose_cat_to_remove$"
        ),
    ],
)
