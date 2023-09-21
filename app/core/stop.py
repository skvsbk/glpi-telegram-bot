import os
from aiogram import types
from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msgid_dict, solve_tickets_dict, close_tickets_dict
from .utilities import delete_inline_keyboard

import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def stop_bot(message: types.Message):
    chat_id = message.chat.id
    try:
        await delete_inline_keyboard(chat_id)
    except:
        pass
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_GOODBY)
    try:
        for filename in ticket_dict[chat_id].attachment:
            if os.path.exists(Config.FILE_PATH + '/' + filename):
                os.remove(Config.FILE_PATH + '/' + filename)
        user_dict.pop(chat_id)
        glpi_dict.pop(chat_id)
        ticket_dict.pop(chat_id)
        msgid_dict.pop(chat_id)
        solve_tickets_dict.pop(chat_id)
        close_tickets_dict.pop(chat_id)

    except:
        logger.warning('execute_on_exit(%s) - error cleaning dictionaries', str(chat_id))
        pass
    finally:
        logger.info('the function execute_on_exit(message) is done for the id %s', str(chat_id))
        pass
