from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
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
from admin.questions_settings.common import (
    choose_q_option,
    CATEGORY,
    back_to_choose_cat,
)
from start import admin_command
import models

QUESTION, CORRECT_CHOICE = range(1, 3)


async def choose_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            context.user_data["category_id_to_add_to"] = int(update.callback_query.data)
        back_buttons = [
            build_back_button("back_to_choose_cat"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text=(
                "أرسل السؤال والإجابات بالصيغة التالية:\n"
                "السؤال؟\n"
                "الإجابة 1\n"
                "الإجابة 2\n"
                "الإجابة 3\n"
                ".\n.\n.\n\n"
                "مثال:\n"
                "<code>ما قيمة 1+1؟\n"
                "2\n0\n3\n4</code>"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return QUESTION


async def get_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        q_data = list(dict.fromkeys(update.message.text.split("\n")).keys())
        q_id = await models.Question.add(
            q=q_data[0],
            category_id=context.user_data["category_id_to_add_to"],
            choices=q_data[1:],
        )
        context.user_data["inserted_q_id"] = q_id
        choices = models.Choice.get_by(q_id=q_id)
        keyboard = [
            [
                InlineKeyboardButton(
                    text=c.choice,
                    callback_data=str(c.id),
                )
            ]
            for c in choices
        ]
        keyboard.append(build_back_button("back_to_get_q"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text="اختر الإجابة الصحيحة لهذا السؤال",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CORRECT_CHOICE


back_to_get_q = choose_cat


async def choose_correct_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await models.Choice.update(
            c_id=int(update.callback_query.data),
            q_id=context.user_data["inserted_q_id"],
            field="is_correct",
            value=True,
        )
        await update.callback_query.answer(
            text="تمت إضافة السؤال بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_q_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^add_q$",
        )
    ],
    states={
        CATEGORY: [
            CallbackQueryHandler(
                choose_cat,
                "^\d+$",
            )
        ],
        QUESTION: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_q,
            )
        ],
        CORRECT_CHOICE: [
            CallbackQueryHandler(
                choose_correct_choice,
                "^\d+$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
        CallbackQueryHandler(back_to_choose_cat, "^back_to_choose_cat$"),
        CallbackQueryHandler(back_to_get_q, "^back_to_get_q$"),
    ],
)
