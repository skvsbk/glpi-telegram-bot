import random
from aiogram import types
from app.config import Config
from app import bot
from app.utils import ticket_dict, msgid_dict, ticket_for_approve
from .utilities import select_action, delete_inline_keyboard, make_keyboard_inline, make_category_keyboard
from .stop import stop_bot
from .inline_tickets_init import reject_ticket_whith_msg

import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def media(message: types.Message):
    if message.chat.type == 'private':
        chat_id = message.chat.id
        try:
            if ticket_dict[chat_id].isnew:
                if message.caption is not None:
                    ticket_dict[chat_id].content += message.caption + ', '
                if message.content_type == 'text':
                    # Delete message with inline keyboard
                    await delete_inline_keyboard(chat_id)
                    # set_ticket_name_or_content(ticket_dict, message, message.text)
                    ticket_dict[chat_id].content += message.text + ', '
                elif message.content_type == 'document':
                    filename = f"{chat_id}_{str(random.randint(0, 1000))}_{message.document.file_name}"
                    await message.document.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[chat_id].attachment.append(filename)
                elif message.content_type == 'photo':
                    photo = message.photo.pop()
                    filename = f"{chat_id}_{str(random.randint(0, 1000))}.jpg"
                    await photo.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[chat_id].attachment.append(filename)
                elif message.content_type == 'video':
                    filename = f"{chat_id}_{str(random.randint(0, 1000))}.mp4"
                    await message.video.download(f"{Config.FILE_PATH}/{filename}")
                    ticket_dict[chat_id].attachment.append(filename)
                else:
                    pass

                kbd_add_send_cancel = {'btn_add': Config.BTN_ADD,
                                       'btn_send': Config.BTN_SEND_TICKET,
                                       'btn_cancel': Config.BTN_CANCEL}

                markup = make_keyboard_inline(2, **kbd_add_send_cancel)

                get_data_msg = await bot.send_message(chat_id=chat_id,
                                                      text=Config.MSG_CAN_ADD,
                                                      parse_mode='html',
                                                      reply_markup=markup)
                msgid_dict[chat_id].append(get_data_msg.message_id)

            # Enter room or equipment
            elif ticket_dict[chat_id].name in (Config.BTN_THEME_EQIPMENT, Config.BTN_THEME_ROOM):
                # Enter name of room or equipment, add it to tickets name
                ticket_name = ticket_dict[chat_id].name + " " + message.text
                ticket_dict[chat_id].name = ticket_name
                # This is the new ticket
                ticket_dict[chat_id].isnew = True
                # Select category keyboard
                await make_category_keyboard(chat_id)

            elif ticket_for_approve[chat_id]:
                await reject_ticket_whith_msg(chat_id, message.text)

            else:
                if len(msgid_dict[chat_id]) > 0:
                    delmsgid = msgid_dict[chat_id].pop()
                    await bot.delete_message(chat_id=chat_id, message_id=delmsgid)
                await bot.send_message(chat_id=chat_id,
                                       text=Config.MSG_KEYBOARD_ATTENTION,
                                       parse_mode='html', reply_markup=None)
                # await make_ticket_title(bot, msgid_dict, message, True)
                await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
        except Exception as err:
            logger.warning('get_data(%s) - some errors: %s', str(chat_id), repr(err))
            logger.warning('Probably the user DID NOT press Start and is NOT AUTORIZED')
            await bot.send_message(chat_id=chat_id,
                                   text=Config.MSG_ERROR_ATTENTION,
                                   parse_mode='html',
                                   reply_markup=None)
            # Delete message with inline keybaord
            try:
                if len(msgid_dict[chat_id]) > 0:
                    delmsgid = msgid_dict[chat_id].pop()
                    await bot.delete_message(chat_id=chat_id, message_id=delmsgid)
            finally:
                await stop_bot(message)
        finally:
            logger.info("the function get_data(message) is done for the id %s", str(chat_id))
