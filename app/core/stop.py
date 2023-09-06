import os
from aiogram import types
from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msgid_dict
from .utils import delete_inline_keyboard

import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def stop(message: types.Message):
    await delete_inline_keyboard(bot, msgid_dict, message.chat.id)
    await bot.send_message(chat_id=message.chat.id,
                           text=Config.MSG_GOODBY)
    try:
        for filename in ticket_dict[message.chat.id].attachment:
            if os.path.exists(Config.FILE_PATH + '/' + filename):
                os.remove(Config.FILE_PATH + '/' + filename)
        user_dict.pop(message.chat.id)
        glpi_dict.pop(message.chat.id)
        ticket_dict.pop(message.chat.id)
        msgid_dict.pop(message.chat.id)
    except:
        logger.warning('execute_on_exit(%s) - error cleaning dictionaries', str(message.chat.id))
        pass
    finally:
        logger.info('the function execute_on_exit(message) is done for the id %s', str(message.chat.id))
        pass
