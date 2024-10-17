from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
    Poll,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from custom_filters import Admin
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from common.constants import *
from common.keyboards import (
    build_admin_keyboard,
    build_back_button,
    build_confirmation_keyboard,
)
from start import admin_command
import models
from admin.channel_test.common import build_channels_keyboard


CHANNEL, CATEGORY, CONFIRM_POST_TEST = range(3)


async def channel_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        await update.callback_query.delete_message()

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="اضغط الزر في الكيبورد لاختيار قناة جديدة، يمكنك أيضاً إرسال آيدي القناة كرسالة.",
            reply_markup=ReplyKeyboardMarkup.from_button(
                button=KeyboardButton(
                    text="اختيار قناة جديدة",
                    request_chat=KeyboardButtonRequestChat(
                        request_id=5, chat_is_channel=True
                    ),
                ),
                resize_keyboard=True,
            ),
        )
        channels = models.Channel.get_by()
        if channels:
            keyboard = build_channels_keyboard(channels=channels)
            keyboard.append(back_to_admin_home_page_button[0])

            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="أو اختر قناة سابقة.",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return CHANNEL


async def get_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        if update.callback_query and update.callback_query.data.startswith("back"):
            await update.callback_query.edit_message_text(
                text="اختر القسم",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CATEGORY

        if update.callback_query:
            channel_id = int(update.callback_query.data)
        elif update.message.chat_shared:
            channel_id = update.message.chat_shared.chat_id
        else:
            channel_id = int(update.message.text)
        try:
            chat = await context.bot.get_chat(chat_id=channel_id)
            stored_chat = models.Channel.get_by(i=channel_id)
            if stored_chat:
                await models.Channel.update(i=chat.id, new_title=chat.title)
            else:
                await models.Channel.add(i=chat.id, title=chat.title)
        except Exception as e:
            print(e)
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="تأكد من أن البوت آدمن في القناة.",
            )
            return

        context.user_data["channel_test_id"] = channel_id

        keyboard = [
            [
                InlineKeyboardButton(
                    text=c.name,
                    callback_data=c.id,
                )
            ]
            for c in models.Category.get_by()
        ]
        keyboard.append(build_back_button("back_to_get_channel"))
        keyboard.append(back_to_admin_home_page_button[0])

        if update.callback_query:
            await update.callback_query.delete_message()

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="تم العثور على القناة ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="اختر القسم",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CATEGORY


back_to_get_channel = channel_test


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            cat_id = int(update.callback_query.data)
            context.user_data["chosen_cat_id"] = cat_id
        else:
            cat_id = context.user_data["chosen_cat_id"]

        cat = models.Category.get_by(cat_id=cat_id)
        ch = models.Channel.get_by(i=context.user_data["channel_test_id"])
        keyboard = build_confirmation_keyboard("post_channel_test")
        keyboard.append(build_back_button("back_to_choose_category"))
        keyboard.append(back_to_admin_home_page_button[0])

        await update.callback_query.edit_message_text(
            text=f"هل أنت متأكد من نشر اختبار في <b>{cat.name}</b> في القناة <b>{ch.title}</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CONFIRM_POST_TEST


back_to_choose_category = get_channel


async def confirm_post_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("yes"):
            questions = models.Question.get_by(
                cat_id=context.user_data["chosen_cat_id"], limit=15
            )

            for q in questions:
                choices = models.Choice.get_by(q_id=q.id)
                await context.bot.send_poll(
                    chat_id=context.user_data["channel_test_id"],
                    question=q.q,
                    type=Poll.QUIZ,
                    options=list(map(lambda x: x.choice, choices)),
                    correct_option_id=(
                        list(filter(lambda x: x.is_correct, choices))[0].id - 1
                    ),
                )
            await update.callback_query.answer(
                text="تم نشر الاختبار في القناة بنجاح ✅",
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


channel_test_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            channel_test,
            "^channel_test$",
        )
    ],
    states={
        CHANNEL: [
            CallbackQueryHandler(
                get_channel,
                "^-?\d+$",
            ),
            MessageHandler(
                filters=filters.Regex("^-?\d+$"),
                callback=get_channel,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=get_channel,
            ),
        ],
        CATEGORY: [
            CallbackQueryHandler(
                choose_category,
                "^\d+$",
            )
        ],
        CONFIRM_POST_TEST: [
            CallbackQueryHandler(
                confirm_post_test,
                "^((yes)|(no)) post_channel_test$",
            )
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        admin_command,
        CallbackQueryHandler(back_to_get_channel, "^back_to_get_channel$"),
        CallbackQueryHandler(back_to_choose_category, "^back_to_choose_category$"),
    ],
)
