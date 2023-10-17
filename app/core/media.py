import random
from aiogram import types
from app.config import Config
from app import bot
from app.utils import ticket_dict, msg_id_dict, ticket_for_approve, ticket_for_comment, project_dict
from .utilities import select_action, delete_inline_keyboard, make_category_keyboard
from .stop import stop_bot
from .inline_tickets_init import reject_ticket_whith_msg, leave_comment

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

                await select_action(chat_id, Config.KBD_ADD_SEND_CANCEL_TICKET, Config.MSG_SELECT_ACTION, True)

            # For project (kaidzen)
            elif project_dict[chat_id].isnew:
                if project_dict[chat_id].name == '':
                    if message.caption is not None:
                        project_dict[chat_id].name = "Проект - " + message.text
                    if message.content_type == 'text':
                        # Delete message with inline keyboard
                        await delete_inline_keyboard(chat_id)
                        project_dict[chat_id].name = "Проект - " + message.text
                    await bot.send_message(chat_id=chat_id,
                                           text=Config.MSG_PROJECT_DESCRIPTION,
                                           reply_markup=None)
                else:
                    if message.caption is not None:
                        project_dict[chat_id].content += message.text + ', '
                    if message.content_type == 'text':
                        # Delete message with inline keyboard
                        await delete_inline_keyboard(chat_id)
                        project_dict[chat_id].content += message.text + ', '
                    elif message.content_type == 'document':
                        filename = f"{chat_id}_{str(random.randint(0, 1000))}_{message.document.file_name}"
                        await message.document.download(f"{Config.FILE_PATH}/{filename}")
                        project_dict[chat_id].attachment.append(filename)
                    elif message.content_type == 'photo':
                        photo = message.photo.pop()
                        filename = f"{chat_id}_{str(random.randint(0, 1000))}.jpg"
                        await photo.download(f"{Config.FILE_PATH}/{filename}")
                        project_dict[chat_id].attachment.append(filename)
                    elif message.content_type == 'video':
                        filename = f"{chat_id}_{str(random.randint(0, 1000))}.mp4"
                        await message.video.download(f"{Config.FILE_PATH}/{filename}")
                        project_dict[chat_id].attachment.append(filename)

                    await select_action(chat_id, Config.KBD_ADD_SEND_CANCEL_KAIDZEN, Config.MSG_SELECT_ACTION, True)

            # Enter room or equipment
            elif ticket_dict[chat_id].name in (Config.BTN_THEME_EQIPMENT, Config.BTN_THEME_ROOM):
                # Enter name of room or equipment, add it to tickets name
                ticket_name = ticket_dict[chat_id].name + " " + message.text
                ticket_dict[chat_id].name = ticket_name
                # This is the new ticket
                ticket_dict[chat_id].isnew = True
                # Select category keyboard
                await make_category_keyboard(chat_id)

            elif ticket_for_approve.get(chat_id):
                await reject_ticket_whith_msg(chat_id, message.text)

            elif ticket_for_comment.get(chat_id):
                await leave_comment(chat_id, message.text)

            else:
                if len(msg_id_dict[chat_id]) > 0:
                    msg_id_for_delete = msg_id_dict[chat_id].pop()
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id_for_delete)
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
                if len(msg_id_dict[chat_id]) > 0:
                    msg_id_for_delete = msg_id_dict[chat_id].pop()
                    await bot.delete_message(chat_id=chat_id, message_id=msg_id_for_delete)
            finally:
                await stop_bot(chat_id)
        finally:
            logger.info("the function get_data(message) is done for the id %s", str(chat_id))
