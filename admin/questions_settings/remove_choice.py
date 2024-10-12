from telegram import Chat, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import models
from admin.questions_settings.q_settings import back_to_q_settings_handler
from common.keyboards import (
    build_back_button,
    build_admin_keyboard,
    build_confirmation_keyboard,
)
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.constants import *
from admin.questions_settings.common import (
    Q,
    CATEGORY,
    choose_q_option,
    choose_cat,
    back_to_choose_cat,
)
from custom_filters import Admin
from start import admin_command
import models

CHOICE_TO_DELETE, CONFIRM_DELETE_CHOICE = range(2, 4)


async def choose_q_to_remove_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_q_id = int(update.callback_query.data)
            context.user_data["q_to_remove_from"] = chosen_q_id
        else:
            chosen_q_id = context.user_data["q_to_remove_from"]

        keyboard = [
            [
                InlineKeyboardButton(
                    text=c.choice,
                    callback_data=str(c.id),
                )
            ]
            for c in models.Choice.get_by(q_id=chosen_q_id)
        ]
        keyboard.append(build_back_button("back_to_choose_q_to_remove_from"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر الإجابة",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOICE_TO_DELETE


back_to_choose_q_to_remove_from = choose_cat


async def choose_choice_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_choice_id = int(update.callback_query.data)
            context.user_data["chosen_choice_id"] = chosen_choice_id
        else:
            chosen_choice_id = context.user_data["chosen_choice_id"]

        choice = models.Choice.get_by(
            c_id=chosen_choice_id,
            q_id=context.user_data["q_to_remove_from"],
        )
        if choice.is_correct:
            keyboard = build_confirmation_keyboard(data="remove_choice")
            keyboard.append(build_back_button("back_to_choose_choice_to_delete"))
            keyboard.append(back_to_admin_home_page_button[0])
            await update.callback_query.edit_message_text(
                text="هذه إجابة السؤال الصحيحة، هل أنت متأكد من أنك تريد حذفها؟",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CONFIRM_DELETE_CHOICE
        await models.Choice.delete(
            choice_id=context.user_data["chosen_choice_id"],
            q_id=context.user_data["q_to_remove_from"],
        )
        await update.callback_query.answer(
            text="تم حذف الإجابة بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


back_to_choose_choice_to_delete = choose_q_to_remove_from


async def confirm_delete_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            await models.Choice.delete(
                choice_id=context.user_data["chosen_choice_id"],
                q_id=context.user_data["q_to_remove_from"],
            )
            await update.callback_query.answer(
                text=(
                    "تم حذف الإجابة بنجاح ✅\n"
                    "عليك تعيين إجابة صحيحة لهذا السؤال عن طريق اختيار أو إضافة إجابة جديدة."
                ),
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


remove_choice_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_q_option,
            "^remove_choice$",
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
                choose_q_to_remove_from,
                "^\d+$",
            )
        ],
        CHOICE_TO_DELETE: [
            CallbackQueryHandler(
                choose_choice_to_delete,
                "^\d+$",
            )
        ],
        CONFIRM_DELETE_CHOICE: [
            CallbackQueryHandler(
                confirm_delete_choice,
                "^((yes)|(no)) remove_choice$",
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        back_to_q_settings_handler,
        CallbackQueryHandler(back_to_choose_cat, "^back_to_choose_cat$"),
        CallbackQueryHandler(
            back_to_choose_choice_to_delete, "^back_to_choose_choice_to_delete$"
        ),
        CallbackQueryHandler(
            back_to_choose_q_to_remove_from, "^back_to_choose_q_to_remove_from$"
        ),
    ],
)
