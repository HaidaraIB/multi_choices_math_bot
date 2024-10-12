from telegram import InlineKeyboardButton


def build_user_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="تحديث رقم الهاتف",
                callback_data="update_phone_number",
            )
        ]
    ]
    return keyboard
