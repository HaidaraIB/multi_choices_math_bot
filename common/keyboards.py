from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
)


def build_user_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="الاختبارات 📝",
                callback_data="take_test",
            )
        ],
        [
            InlineKeyboardButton(
                text="الإعدادات ⚙️",
                callback_data="user_settings",
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن ⚙️🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="إعدادات الأسئلة ⚙️❔",
                callback_data="q settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="اختبار في قناة 📢📝",
                callback_data="channel_test",
            )
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_button(data: str):
    return [InlineKeyboardButton(text="الرجوع🔙", callback_data=data)]


def build_request_buttons():
    keyboard = [
        [
            KeyboardButton(
                text="معرفة id مستخدم🆔",
                request_users=KeyboardButtonRequestUsers(
                    request_id=0, user_is_bot=False
                ),
            ),
            KeyboardButton(
                text="معرفة id قناة📢",
                request_chat=KeyboardButtonRequestChat(
                    request_id=1, chat_is_channel=True
                ),
            ),
        ],
        [
            KeyboardButton(
                text="معرفة id مجموعة👥",
                request_chat=KeyboardButtonRequestChat(
                    request_id=2, chat_is_channel=False
                ),
            ),
            KeyboardButton(
                text="معرفة id بوت🤖",
                request_users=KeyboardButtonRequestUsers(
                    request_id=3, user_is_bot=True
                ),
            ),
        ],
    ]
    return keyboard


def build_confirmation_keyboard(data: str):
    keyboard = [
        [
            InlineKeyboardButton(
                text="نعم 👍",
                callback_data=f"yes {data}",
            ),
            InlineKeyboardButton(
                text="لا 👎",
                callback_data=f"no {data}",
            ),
        ],
    ]
    return keyboard
