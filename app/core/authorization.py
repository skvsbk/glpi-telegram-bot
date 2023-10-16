from aiogram import types
from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msg_id_dict, project_dict
from app.utils import glpiapi, glpidb
from .utilities import select_action, delete_inline_keyboard
from .stop import stop_bot

import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def authorization(message: types.Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    if phone[0] != '+':
        phone = '+' + phone
    # Modify phone from +7XXXXXXXXXX to +7 (XXX) XXX-XX-XX
    phone_for_send = f'{phone[0:2]} ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:]}'
    # Get user's credentials and continue if phone number contains in DB, else send /stop command
    user_credentials = glpidb.get_user_credentials(phone_for_send)
    if user_credentials and user_credentials['user_token']:
        # Save telegramid to user profile
        if user_credentials['telegramid'] in ('', None):
            glpidb.put_telegramid_for_user(user_credentials['id'], chat_id)

        # Fill user_dict
        user_dict[chat_id] = glpiapi.User(user_id=user_credentials['id'],
                                          token=user_credentials['user_token'],
                                          locations_name=user_credentials['locations_name'])
        # Get user session
        glpi_dict[chat_id] = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user_dict[chat_id])
        if glpi_dict[chat_id].session is None:
            await bot.send_message(chat_id=chat_id,
                                   text=Config.MSG_AUTH_ERROR,
                                   reply_markup=None)
            logger.warning('authorization(message) error for id %s and phone %s - empty user.session',
                           str(chat_id), phone_for_send)
            await stop_bot(message)
            return

        # Create empty ticket
        ticket_dict[chat_id] = glpiapi.Ticket()

        # Create empty ticket (kaidzen)
        project_dict[chat_id] = glpiapi.Project()

        # This is for delete keyboard
        msg_id_dict[chat_id] = [message.message_id]

        item_remove = types.ReplyKeyboardRemove()
        await bot.send_message(chat_id=chat_id,
                               text=f"{Config.MSG_WELLCOME}, {user_credentials['firstname']}!",
                               reply_markup=item_remove)
        await bot.send_message(chat_id=chat_id,
                               text=Config.MSG_INTRODUCTION,
                               reply_markup=None)
        # Next step
        await delete_inline_keyboard(chat_id)
        await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
    else:
        await bot.send_message(chat_id=chat_id,
                               text=Config.MSG_AUTH_ERROR,
                               reply_markup=None)
        logger.warning('read_contact_phone(message) Authorisation Error for id %s and phone %s',
                       str(chat_id), phone_for_send)
        await stop_bot(message)
