from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import models
from common.keyboards import build_back_button
from common.back_to_home_page import back_to_admin_home_page_button
from custom_filters import Admin


def build_q_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة مجموعة ➕",
                callback_data="add_cat",
            ),
            InlineKeyboardButton(
                text="حذف مجموعة ✖️",
                callback_data="remove_cat",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إضافة سؤال ➕",
                callback_data="add_q",
            ),
            InlineKeyboardButton(
                text="حذف سؤال ✖️",
                callback_data="remove_q",
            ),
        ],
        [
            InlineKeyboardButton(
                text="تعديل سؤال ♻️",
                callback_data="update_q",
            ),
        ],
        [
            InlineKeyboardButton(
                text="إضافة إجابة ➕",
                callback_data="add_choice",
            ),
            InlineKeyboardButton(
                text="حذف إجابة ✖️",
                callback_data="remove_choice",
            ),
        ],
    ]
    return keyboard


CATEGORY, Q = range(2)


async def choose_q_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        categories = models.Category.get_by()
        if not categories:
            await update.callback_query.answer(
                text="ليس لديك مجموعات بعد ❗️",
                show_alert=True,
            )
            return
        keyboard = [
            [
                InlineKeyboardButton(
                    text=c.name,
                    callback_data=str(c.id),
                )
            ]
            for c in categories
        ]
        keyboard.append(build_back_button("back_to_q_settings"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر المجموعة",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CATEGORY


async def choose_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            chosen_cat_id = int(update.callback_query.data)
            context.user_data["chosen_cat_id"] = chosen_cat_id
        else:
            chosen_cat_id = context.user_data["chosen_cat_id"]
        questions = models.Question.get_by(cat_id=chosen_cat_id)
        if not questions:
            await update.callback_query.answer(
                text="ليس لديك أسئلة بعد ❗️",
                show_alert=True,
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text=q.q,
                    callback_data=str(q.id),
                )
            ]
            for q in questions
        ]
        keyboard.append(build_back_button("back_to_choose_cat"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر السؤال",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return Q


back_to_choose_cat = choose_q_option
