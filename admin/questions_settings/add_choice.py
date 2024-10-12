from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.constants import *
from common.keyboards import (
    build_back_button,
    build_admin_keyboard,
    build_confirmation_keyboard,
)
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from custom_filters import Admin
from admin.questions_settings.common import (
    choose_cat,
    choose_q_option,
    back_to_choose_cat,
    Q,
    CATEGORY,
)
from admin.questions_settings.q_settings import back_to_q_settings_handler
import models
from start import admin_command

CHOICE, IS_CORRECT = range(2, 4)


async def choose_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_q_id = int(update.callback_query.data)
            context.user_data["chosen_q_id"] = chosen_q_id
        else:
            chosen_q_id = context.user_data["chosen_q_id"]

        back_buttons = [
            build_back_button("back_to_choose_q"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل الإجابة الجديدة",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return CHOICE


back_to_choose_q = choose_cat


async def get_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_confirmation_keyboard(data="correct_choice")
        keyboard.append(build_back_button("back_to_get_choice"))
        keyboard.append(back_to_admin_home_page_button[0])
        if update.message:
            choice = update.message.text
            context.user_data["choice_to_add"] = choice
            await update.message.reply_text(
                text=(f"هل\n" f"<b>{choice}</b>\n" "هي الإجابة الصحيحة؟"),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            choice = context.user_data["choice_to_add"]
            await update.callback_query.edit_message_text(
                text=(f"هل\n" f"<b>{choice}</b>\n" "هي الإجابة الصحيحة؟"),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return IS_CORRECT


back_to_get_choice = choose_q


async def choose_is_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            await models.Choice.add(
                choice=context.user_data["choice_to_add"],
                q_id=context.user_data["chosen_q_id"],
                is_correct=True,
            )
        else:
            await models.Choice.add(
                choice=context.user_data["choice_to_add"],
                q_id=context.user_data["chosen_q_id"],
            )

        await update.callback_query.answer(
            text="تمت إضافة الإجابة بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_choice_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^add_choice$",
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
                choose_q,
                "^\d+$",
            )
        ],
        CHOICE: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_choice,
            ),
        ],
        IS_CORRECT: [
            CallbackQueryHandler(choose_is_correct, "^((yes)|(no)) correct_choice$")
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
        CallbackQueryHandler(back_to_choose_cat, "^back_to_choose_cat$"),
        CallbackQueryHandler(back_to_choose_q, "^back_to_choose_q$"),
        CallbackQueryHandler(back_to_get_choice, "^back_to_get_choice$"),
    ],
)
