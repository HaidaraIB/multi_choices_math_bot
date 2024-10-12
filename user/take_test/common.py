from telegram import InlineKeyboardButton, Poll
from telegram.ext import ContextTypes
import models
from common.stringifies import calc_result, stringify_test_result


def build_test_options_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="بدء الاختبار",
                callback_data="start_test",
            )
        ]
    ]
    return keyboard


async def finish_test(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    test_id = await models.TestResult.add(
        user_id=user_id,
        cat_id=context.user_data["test_cat_id"],
        result=calc_result(context),
    )
    await models.TestQuestion.add(
        q_ids=context.user_data["test_q_ids"],
        cat_id=context.user_data["test_cat_id"],
        test_id=test_id,
    )
    await context.bot.send_message(
        chat_id=user_id,
        text=stringify_test_result(context),
    )
    context.user_data["test_running"] = False


async def send_question_on_timeout(context: ContextTypes.DEFAULT_TYPE):
    context.user_data["timeout_count"] += 1
    try:
        prev_q_id_idx = context.user_data["test_q_ids"].index(
            context.user_data["currect_q_id"]
        )
        context.user_data["currect_q_id"] = context.user_data["test_q_ids"][
            prev_q_id_idx + 1
        ]
    except:
        await finish_test(context=context, user_id=context.job.user_id)
        return
    curr_q = models.Question.get_by(q_id=context.user_data["currect_q_id"])
    choices = models.Choice.get_by(q_id=curr_q.id)

    if curr_q:
        context.user_data["currect_correct_choice_id"] = (
            list(filter(lambda x: x.is_correct, choices))[0].id - 1
        )
        await context.bot.send_poll(
            chat_id=context.job.user_id,
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
            name=f"send_question_on_timeout_{context.job.user_id}",
            user_id=context.job.user_id,
        )
