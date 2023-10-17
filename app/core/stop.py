import os
from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msg_id_dict, tickets_for_solve_dict, tickets_for_close_dict
from app.utils import project_dict
from .utilities import delete_inline_keyboard

import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def stop_bot(chat_id):
    try:
        await delete_inline_keyboard(chat_id)
    except:
        pass
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_GOODBY)

    dicts_for_clear = [user_dict,
                       glpi_dict,
                       ticket_dict,
                       project_dict,
                       msg_id_dict,
                       tickets_for_solve_dict,
                       tickets_for_close_dict
                       ]
    try:
        for filename in ticket_dict[chat_id].attachment:
            if os.path.exists(Config.FILE_PATH + '/' + filename):
                os.remove(Config.FILE_PATH + '/' + filename)
        for item in dicts_for_clear:
            if item.get(chat_id):
                item.pop(chat_id)

    except:
        logger.warning('execute_on_exit(%s) - error cleaning dictionaries', str(chat_id))
    finally:
        logger.info('the function execute_on_exit(message) is done for the id %s', str(chat_id))
