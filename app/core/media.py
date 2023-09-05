import random
from aiogram import types
from app.config import Config
from app import bot
from app.utils import ticket_dict, msgid_dict
from .utils import make_ticket_title, delete_inline_keyboard, make_keyboard_inline, make_category_keyboard
from .stop import stop

import logging


# logging
logging.basicConfig(level=logging.WARNING, filename='glpibot.log',
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def media(message: types.Message):
    if message.chat.type == 'private':
        try:
            if ticket_dict[message.chat.id].isnew:
                if message.caption is not None:
                    ticket_dict[message.chat.id].content += message.caption + ', '
                if message.content_type == 'text':
                    # Delete message with inline keyboard
                    await delete_inline_keyboard(bot, msgid_dict, message.chat.id)
                    # set_ticket_name_or_content(ticket_dict, message, message.text)
                    ticket_dict[message.chat.id].content += message.text + ', '
                elif message.content_type == 'document':
                    filename = f"{message.chat.id}_{str(random.randint(0, 1000))}_{message.document.file_name}"
                    await message.document.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[message.chat.id].attachment.append(filename)
                elif message.content_type == 'photo':
                    photo = message.photo.pop()
                    filename = f"{message.chat.id}_{str(random.randint(0, 1000))}.jpg"
                    await photo.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[message.chat.id].attachment.append(filename)
                    # print(f"{FILE_PATH}/{filename}")
                    # print('ticket_dict', message.chat.id, filename)
                elif message.content_type == 'video':
                    filename = f"{message.chat.id}_{str(random.randint(0, 1000))}.mp4"
                    await message.video.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[message.chat.id].attachment.append(filename)
                else:
                    pass

                kbd_add_send_cancel = {'btn_add': Config.BTN_ADD,
                                       'btn_send': Config.BTN_SEND_TICKET,
                                       'btn_cancel': Config.BTN_CANCEL}

                markup = make_keyboard_inline(2, **kbd_add_send_cancel)

                get_data_msg = await bot.send_message(chat_id=message.chat.id,
                                                      text=Config.MSG_CAN_ADD,
                                                      parse_mode='html',
                                                      reply_markup=markup)
                msgid_dict[message.chat.id].append(get_data_msg.message_id)

            # Enter room or equipment
            elif ticket_dict[message.chat.id].name in (Config.BTN_THEME_EQIPMENT, Config.BTN_THEME_ROOM):
                # Enter name of room or equipment, add it to tickets name
                ticket_name = ticket_dict[message.chat.id].name + " " + message.text
                ticket_dict[message.chat.id].name = ticket_name
                # This is the new ticket
                ticket_dict[message.chat.id].isnew = True
                # Select category keyboard
                await make_category_keyboard(bot, msgid_dict, message)

            else:
                if len(msgid_dict[message.chat.id]) > 0:
                    delmsgid = msgid_dict[message.chat.id].pop()
                    await bot.delete_message(chat_id=message.chat.id, message_id=delmsgid)
                await bot.send_message(chat_id=message.chat.id,
                                       text=Config.MSG_KEYBOARD_ATTENTION,
                                       parse_mode='html', reply_markup=None)
                await make_ticket_title(bot, msgid_dict, message, True)
        except Exception as err:
            logger.warning('get_data(%s) - some errors: %s', str(message.chat.id), repr(err))
            logger.warning('Probably the user DID NOT press Start and is NOT AUTORIZED')
            await bot.send_message(chat_id=message.chat.id,
                                   text=Config.MSG_ERROR_ATTENTION,
                                   parse_mode='html',
                                   reply_markup=None)
            # Delete message with inline keybaord
            try:
                if len(msgid_dict[message.chat.id]) > 0:
                    delmsgid = msgid_dict[message.chat.id].pop()
                    await bot.delete_message(chat_id=message.chat.id, message_id=delmsgid)
            finally:
                await stop(message)
        finally:
            logger.info("the function get_data(message) is done for the id %s", str(message.chat.id))
