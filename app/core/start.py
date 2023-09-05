from aiogram import types
from app.config import Config
from app import bot


async def start(message: types.Message):
    keyboard_send_phone = types.ReplyKeyboardMarkup(row_width=1)
    botton_send_phone = types.KeyboardButton(Config.BTN_SEND_NUMBER, request_contact=True)
    keyboard_send_phone.add(botton_send_phone)
    await bot.send_message(chat_id=message.chat.id,
                           text=Config.MSG_AUTH_ATTENTION,
                           parse_mode='html',
                           reply_markup=keyboard_send_phone)
