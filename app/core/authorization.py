from aiogram import types
from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msgid_dict
from app.utils import glpiapi, glpidb
from .utils import make_ticket_title
from .stop import stop

import logging


# logging
logging.basicConfig(level=logging.WARNING, filename='glpibot.log',
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def authorization(message: types.Message):
    phone = message.contact.phone_number
    if phone[0] != '+':
        phone = '+' + phone
    # Modify phone form +7XXXXXXXXXX to +7 (XXX) XXX-XX-XX
    phone_for_send = f'{phone[0:2]} ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:]}'
    # Get user's credentials and continue if phone number contains in DB, else send /stop command
    user_credentials = glpidb.get_user_credentials(phone_for_send)  # dictionary with keys 'user_token' 'id' 'firstname'
    if user_credentials and user_credentials['user_token']:
        user_dict[message.chat.id] = glpiapi.User(user_id=user_credentials['id'],
                                                  token=user_credentials['user_token'],
                                                  locations_name=user_credentials['locations_name'])
        # Get user session
        glpi_dict[message.chat.id] = glpiapi.GLPI(url=Config.URL_GLPI, user=user_dict[message.chat.id])
        if glpi_dict[message.chat.id].session is None:
            await bot.send_message(chat_id=message.chat.id,
                                   text=Config.MSG_AUTH_ERROR,
                                   reply_markup=None)
            logger.warning('read_contact_phone(message) Authorisation Error for id %s and phone %s',
                           str(message.chat.id), phone_for_send)
            await stop(message)
            return

        # Create empty ticket
        ticket_dict[message.chat.id] = glpiapi.Ticket()
        msgid_dict[message.chat.id] = [message.message_id]

        item_remove = types.ReplyKeyboardRemove()
        await bot.send_message(chat_id=message.chat.id,
                               text=f"{Config.MSG_WELLCOME}, {user_credentials['firstname']}!",
                               reply_markup=item_remove)
        await bot.send_message(chat_id=message.chat.id,
                               text=Config.MSG_INTRODUCTION,
                               reply_markup=None)
        await make_ticket_title(bot, msgid_dict, message, True)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=Config.MSG_AUTH_ERROR,
                               reply_markup=None)
        logger.warning('read_contact_phone(message) Authorisation Error for id %s and phone %s',
                       str(message.chat.id), phone_for_send)
        await stop(message)
