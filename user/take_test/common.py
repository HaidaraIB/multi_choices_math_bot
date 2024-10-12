from telegram import InlineKeyboardButton
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
