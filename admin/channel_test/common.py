from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import models


def build_channels_keyboard():
    channels = models.Channel.get_by()
    keyboard: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(channels), 2):
        row = []
        row.append(
            InlineKeyboardButton(
                text=channels[i].title,
                callback_data=str(channels[i].id),
            )
        )
        if i + 1 < len(channels):
            row.append(
                InlineKeyboardButton(
                    text=channels[i + 1].title,
                    callback_data=str(channels[i + 1].id),
                )
            )
        keyboard.append(row)
    return keyboard
