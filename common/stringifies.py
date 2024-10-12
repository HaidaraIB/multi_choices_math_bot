import models
from telegram.ext import ContextTypes
from common.common import format_float


def stringify_user(user: models.User):
    return (
        f"معلومات مستخدم:\n\n"
        f"آيدي: <code>{user.id}</code>\n"
        f"يوزر: {'@' + user.username if user.username else 'لا يوجد'}\n"
        f"اسم: <b>{user.name}</b>\n"
        f"رقم هاتف: <code>{user.phone_number}</code>"
    )


def calc_result(context: ContextTypes.DEFAULT_TYPE):
    multiplier = 100 / (
        context.user_data["correct_count"] + context.user_data["incorrect_count"]
    )
    result = format_float(context.user_data["correct_count"] * multiplier)
    return result


def stringify_test_result(context: ContextTypes.DEFAULT_TYPE):
    result = calc_result(context)
    return (
        "🏁 انتهى الاختبار 🏁\n\n"
        f"✅ الإجابات الصحيحة: <b>{context.user_data['correct_count']}</b>\n"
        f"❌ الإجابات الخاطئة: <b>{context.user_data['incorrect_count']}</b>\n"
        f"🔢 العلامة:\n<b>{f'{result} / 100'}</b>"
    )
