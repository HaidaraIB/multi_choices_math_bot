from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
import models
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.constants import *
from common.keyboards import build_back_button, build_admin_keyboard
from admin.questions_settings.common import (
    CATEGORY,
    Q,
    choose_q_option,
    choose_cat,
    back_to_choose_cat,
)
from admin.questions_settings.q_settings import back_to_q_settings_handler
from start import admin_command

UPDATE_Q_OPTION, NEW_Q, NEW_CORRECT_CHOICE = range(2, 5)


async def choose_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_q_id = int(update.callback_query.data)
            context.user_data["chosen_q_id"] = chosen_q_id
        else:
            chosen_q_id = context.user_data["chosen_q_id"]

        keyboard = [
            [
                InlineKeyboardButton(text="نص السؤال", callback_data="update q_q"),
                InlineKeyboardButton(
                    text="الإجابة الصحيحة", callback_data="update q_is_correct"
                ),
            ],
            build_back_button("back_to_update_q"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="ما الذي تريد تعديله؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return UPDATE_Q_OPTION


back_to_update_q = choose_cat


async def choose_update_q_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            update_option = update.callback_query.data.replace("update q_", "")
            context.user_data["update_q_option"] = update_option
        else:
            update_option = context.user_data["update_q_option"]

        if update_option == "q":
            text = "أرسل نص السؤال الجديد"
            keyboard = [
                build_back_button("back_to_choose_update_q_option"),
                back_to_admin_home_page_button[0],
            ]
            ret = NEW_Q
        elif update_option == "is_correct":
            text = "اختر الإجابة الصحيحة الجديدة"
            choices = models.Choice.get_by(q_id=context.user_data["chosen_q_id"])
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=c.choice,
                        callback_data=str(c.id),
                    )
                ]
                for c in choices
            ]
            keyboard.append(build_back_button("back_to_choose_update_q_option"))
            keyboard.append(back_to_admin_home_page_button[0])
            ret = NEW_CORRECT_CHOICE

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ret


back_to_choose_update_q_option = choose_q


async def get_new_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        new_q = update.message.text
        await models.Question.update(
            q_id=context.user_data["chosen_q_id"],
            field="q",
            value=new_q,
        )
        await update.message.reply_text(
            text="تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


async def choose_new_correct_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        c_id = int(update.callback_query.data)
        await models.Choice.update(
            c_id=c_id,
            q_id=context.user_data["chosen_q_id"],
            field="is_correct",
            value=True,
        )
        await update.callback_query.answer(
            text="تمت العملية بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


update_q_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^update_q$",
        )
    ],
    states={
        CATEGORY: [
            CallbackQueryHandler(
                choose_cat,
                "^\d+$",
            ),
        ],
        Q: [
            CallbackQueryHandler(
                choose_q,
                "^\d+$",
            )
        ],
        UPDATE_Q_OPTION: [
            CallbackQueryHandler(
                choose_update_q_option,
                "^update q_",
            ),
        ],
        NEW_Q: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_new_q,
            )
        ],
        NEW_CORRECT_CHOICE: [
            CallbackQueryHandler(
                choose_new_correct_choice,
                "^\d+$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_q_settings_handler,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_choose_cat, "^back_to_choose_cat$"),
        CallbackQueryHandler(back_to_update_q, "^back_to_update_q$"),
        CallbackQueryHandler(
            back_to_choose_update_q_option, "^back_to_choose_update_q_option$"
        ),
    ],
)
