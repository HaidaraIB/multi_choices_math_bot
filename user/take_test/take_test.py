from telegram import Update, Poll, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    PollAnswerHandler,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
)
import models
from user.take_test.common import (
    build_test_options_keyboard,
    finish_test,
    send_question_on_timeout,
)
from common.back_to_home_page import back_to_user_home_page_button
from common.keyboards import build_back_button
import asyncio
from datetime import datetime

CATEGORY, TEST_OPTION, TEST = range(3)


async def take_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if context.user_data.get("test_running", False):
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="المعذرة، مازال لديك اختبار قيد التشغيل حالياً. يرجى إيقاف الاختبار الحالي عبر إرسال /cancel_test.",
            )
            return
        keyboard = [
            [
                InlineKeyboardButton(
                    text=c.name,
                    callback_data=c.id,
                )
            ]
            for c in models.Category.get_by()
        ]
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="اختر القسم",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CATEGORY


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        cat_id = int(update.callback_query.data)
        context.user_data["test_cat_id"] = cat_id

        questions = models.Question.get_by(cat_id=cat_id, limit=15)
        if not questions:
            await update.callback_query.answer(
                text="ليس لدينا أسئلة في هذا القسم بعد ❗️",
                show_alert=True,
            )
            return

        cat = models.Category.get_by(cat_id=cat_id)
        keyboard = build_test_options_keyboard()
        keyboard.append(build_back_button("back_to_choose_category"))
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=(
                f"القسم المختار: <b>{cat.name}</b>\n"
                f"مدة الاختبار 15 دقيقة، دقيقة لكل سؤال.\n"
                "عدد الأسئلة 15 سؤال.\n"
                "ستظهر الأسئلة واحداً تلو الآخر.\n"
                "لا يمكنك تغيير الإجابة بعد اختيارها.\n"
                "سيتم احتساب العلامة النهائية من 100 بعد نهاية الاختبار على الفور.\n"
                "يمكنك إلغاء الاختبار بالضغط على الأمر /cancel_test\n\n"
                "هل تود بدء هذا الاختبار؟"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return TEST_OPTION


back_to_choose_category = take_test


async def choose_test_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and not context.user_data.get(
        "test_running", False
    ):

        questions = models.Question.get_by(
            cat_id=context.user_data["test_cat_id"], limit=15
        )
        curr_q = questions[0]
        choices = models.Choice.get_by(q_id=curr_q.id)

        context.user_data["test_q_ids"] = list(map(lambda x: x.id, questions))
        context.user_data["currect_q_id"] = curr_q.id
        context.user_data["currect_correct_choice_id"] = (
            list(filter(lambda x: x.is_correct, choices))[0].id - 1
        )
        context.user_data["correct_count"] = 0
        context.user_data["incorrect_count"] = 0
        context.user_data["timeout_count"] = 0
        context.user_data["test_running"] = True

        test_run_in_text = "سيبدأ الاختبار بعد: "
        for i in range(3, 0, -1):
            await update.callback_query.edit_message_text(
                text=test_run_in_text + f"<b>{i}</b>"
            )
            await asyncio.sleep(1)
        await update.callback_query.delete_message()

        await context.bot.send_poll(
            chat_id=update.effective_user.id,
            question=curr_q.q,
            type=Poll.QUIZ,
            is_anonymous=False,
            options=list(map(lambda x: x.choice, choices)),
            correct_option_id=context.user_data["currect_correct_choice_id"],
            open_period=10,
        )
        context.job_queue.run_once(
            send_question_on_timeout,
            when=10,
            name=f"send_question_on_timeout_{update.effective_user.id}",
            user_id=update.effective_user.id,
        )

        context.user_data["test_begin_time"] = datetime.now()
        return TEST


async def choose_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.get_jobs_by_name(
        f"send_question_on_timeout_{update.effective_user.id}"
    )
    if jobs:
        jobs[0].schedule_removal()
    if (
        update.poll_answer.option_ids[0]
        == context.user_data["currect_correct_choice_id"]
    ):
        context.user_data["correct_count"] += 1
    else:
        context.user_data["incorrect_count"] += 1

    try:
        prev_q_id_idx = context.user_data["test_q_ids"].index(
            context.user_data["currect_q_id"]
        )
        context.user_data["currect_q_id"] = context.user_data["test_q_ids"][
            prev_q_id_idx + 1
        ]
    except:
        await finish_test(context=context, user_id=update.effective_user.id)
        return ConversationHandler.END

    curr_q = models.Question.get_by(q_id=context.user_data["currect_q_id"])
    choices = models.Choice.get_by(q_id=curr_q.id)

    if curr_q:
        context.user_data["currect_correct_choice_id"] = (
            list(filter(lambda x: x.is_correct, choices))[0].id - 1
        )
        await context.bot.send_poll(
            chat_id=update.effective_user.id,
            question=curr_q.q,
            type=Poll.QUIZ,
            is_anonymous=False,
            options=list(map(lambda x: x.choice, choices)),
            correct_option_id=context.user_data["currect_correct_choice_id"],
            open_period=10,
        )
        context.job_queue.run_once(
            send_question_on_timeout,
            when=10,
            name=f"send_question_on_timeout_{update.effective_user.id}",
            user_id=update.effective_user.id,
        )

    else:
        await finish_test(context=context, user_id=update.effective_user.id)
        return ConversationHandler.END


async def cancel_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        jobs = context.job_queue.get_jobs_by_name(
            f"send_question_on_timeout_{update.effective_user.id}"
        )
        if jobs:
            jobs[0].schedule_removal()
        context.user_data["test_running"] = False
        await update.message.reply_text(text="تم إلغاء الاختبار ✅")
        return ConversationHandler.END


cancel_test_command = CommandHandler("cancel_test", cancel_test)

take_test_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            take_test,
            "^take_test$",
        )
    ],
    states={
        CATEGORY: [
            CallbackQueryHandler(
                choose_category,
                "^\d+$",
            )
        ],
        TEST_OPTION: [
            CallbackQueryHandler(
                choose_test_option,
                "^start_test$",
            )
        ],
        TEST: [
            PollAnswerHandler(choose_answer),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_choose_category, "^back_to_choose_category$"),
        cancel_test_command,
    ],
    per_chat=False,
    allow_reentry=True,
)
