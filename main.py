from aiogram import Dispatcher, executor
import logging.config
from app import bot
from app.core import start, authorization, stop, media
from app.core.inline_keyboard import callback_inline_keyboard
from app.config import Config


logging.config.dictConfig(Config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

dp = Dispatcher(bot)
dp.message_handler(commands=['start'])(start.start)
dp.message_handler(content_types=['contact'])(authorization.authorization)
dp.message_handler(commands=['stop'])(stop.stop)
dp.message_handler(content_types=['text', 'photo', 'video', 'document'])(media.media)
dp.callback_query_handler(lambda callback_query: True)(callback_inline_keyboard)


if __name__ == "__main__":
    # run bot
    executor.start_polling(dp, skip_updates=True)
