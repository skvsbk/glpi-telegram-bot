import os
import random

from aiogram import Bot, Dispatcher, executor, types
from config import Config
import glpidb
import glpiapi
from keyboard import select_ticket_title, delete_inline_keyboard, make_keyboard_inline
import logging


# logging
logging.basicConfig(level=logging.WARNING, filename='glpibot.log',
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(bot)

# Dicts for each message.chat.id (for each user)
user_dict = dict()
ticket_dict = dict()
glpi_dict = dict()
msgid_dict = {"": []}


# Registration
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard_send_phone = types.ReplyKeyboardMarkup(row_width=1)
    botton_send_phone = types.KeyboardButton(Config.BTN_SEND_NUMBER, request_contact=True)
    keyboard_send_phone.add(botton_send_phone)
    await bot.send_message(chat_id=message.chat.id,
                           text=Config.MSG_AUTH_ATTENTION,
                           parse_mode='html',
                           reply_markup=keyboard_send_phone)


@dp.message_handler(content_types=['contact'])
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
        await select_ticket_title(bot, msgid_dict, message, True)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=Config.MSG_AUTH_ERROR,
                               reply_markup=None)
        logger.warning('read_contact_phone(message) Authorisation Error for id %s and phone %s',
                       str(message.chat.id), phone_for_send)
        await stop(message)


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
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


@dp.message_handler(content_types=['text', 'photo', 'video', 'document'])
async def get_media(message: types.Message):
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

                kbd_add_send_cancel = {'btn_continue': Config.BTN_ADD,
                                       'btn_send': Config.BTN_SEND_TICKET,
                                       'btn_cancel': Config.BTN_CANCEL}

                markup = make_keyboard_inline(2, **kbd_add_send_cancel)

                get_data_msg = await bot.send_message(chat_id=message.chat.id,
                                                      text=Config.MSG_CAN_ADD,
                                                      parse_mode='html',
                                                      reply_markup=markup)
                msgid_dict[message.chat.id].append(get_data_msg.message_id)

            # Enter room or equipment
            elif (ticket_dict[message.chat.id].name == Config.BTN_THEME_EQIPMENT
                  or ticket_dict[message.chat.id].name == Config.BTN_THEME_ROOM):
                # Enter name of room or equipment, add it to tickets name
                ticket_name = ticket_dict[message.chat.id].name + " " + message.text
                ticket_dict[message.chat.id].name = ticket_name
                # This is the new ticket
                ticket_dict[message.chat.id].isnew = True

                # Select category
                kbd_category = {'btn_category_1': Config.KBD_CATEGORY['btn_category_1'][0],
                                'btn_category_2': Config.KBD_CATEGORY['btn_category_2'][0],
                                'btn_category_3': Config.KBD_CATEGORY['btn_category_3'][0],
                                'btn_category_4': Config.KBD_CATEGORY['btn_category_4'][0],
                                'btn_category_5': Config.KBD_CATEGORY['btn_category_5'][0],
                                'btn_category_6': Config.KBD_CATEGORY['btn_category_6'][0]
                                }
                markup = make_keyboard_inline(2, **kbd_category)

                title_msg = await bot.send_message(chat_id=message.chat.id,
                                                   text=Config.MSG_SELECT_TYPE,
                                                   reply_markup=markup)
                msgid_dict[message.chat.id].append(title_msg.message_id)

            else:
                if len(msgid_dict[message.chat.id]) > 0:
                    delmsgid = msgid_dict[message.chat.id].pop()
                    await bot.delete_message(chat_id=message.chat.id, message_id=delmsgid)
                await bot.send_message(chat_id=message.chat.id,
                                       text=Config.MSG_KEYBOARD_ATTENTION,
                                       parse_mode='html', reply_markup=None)
                await select_ticket_title(bot, msgid_dict, message, True)
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


# Pushing inline keyboard
@dp.callback_query_handler(lambda callback_query: True)
async def callback_inline_keyboard(call):
    try:
        if call.message:
            if call.data == 'btn_theme_equipment' or call.data == 'btn_theme_room':
                # save choice to dict or object Ticket
                if call.data == 'btn_theme_equipment':
                    ticket_dict[call.message.chat.id].name = Config.BTN_THEME_EQIPMENT
                else:
                    ticket_dict[call.message.chat.id].name = Config.BTN_THEME_ROOM
                # Delete inlaine keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                # send message
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='Тема: ' + ticket_dict[call.message.chat.id].name)
                await bot.send_message(chat_id=call.message.chat.id,
                                       text=Config.MSG_ENTER_NAME)

            elif call.data == 'btn_continue':
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            text="Опишите проблему, сделайте фото или видео...",
                                            reply_markup=None)
            elif call.data == 'btn_send':
                # Delete message with inline keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)
                await bot.send_chat_action(chat_id=call.message.chat.id, action='upload_document')
                # send ticket
                glpi_dict[call.message.chat.id].ticket = ticket_dict[call.message.chat.id]
                ticket_id = glpi_dict[call.message.chat.id].create_ticket()
                ticket_dict[call.message.chat.id].id = ticket_id
                # upload files/photos/videos to glpi
                for filename in ticket_dict[call.message.chat.id].attachment:
                    # print(filename)
                    doc_id = glpi_dict[call.message.chat.id].upload_doc(Config.FILE_PATH, filename)
                    if doc_id is not None:
                        # update table glpi_documents_items
                        glpidb.update_doc_item(doc_id, ticket_id, user_dict[call.message.chat.id].id)
                if ticket_id is not None:
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text="Заявка №" + str(ticket_id) + " успешно оформлена",
                                           reply_markup=None)
                else:
                    await bot.send_message(chat_id=call.message.chat.id,
                                           text=Config.MSG_ERROR_SEND,
                                           reply_markup=None)
                await stop(call.message)

            elif call.data == 'btn_cancel' or call.data == 'btn_theme_exit':
                if ticket_dict[call.message.chat.id].name == '':
                    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                else:
                    await bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id=call.message.message_id,
                                                text=Config.MSG_CANCEL,
                                                reply_markup=None)
                await stop(call.message)

            # Select category
            elif call.data.startswith('btn_category_'):
                # Set category_id in Ticket object
                btn_name = call.data
                category_id = Config.KBD_CATEGORY[btn_name][1]
                ticket_dict[call.message.chat.id].category_id = category_id

                # Delete message with inline keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                # send message
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='Категория: ' + Config.KBD_CATEGORY[btn_name][0])

                # Display urgency
                kbd_urgency = {'btn_urgency_1': Config.KBD_URGENCY['btn_urgency_1'][0],
                               'btn_urgency_2': Config.KBD_URGENCY['btn_urgency_2'][0],
                               'btn_urgency_3': Config.KBD_URGENCY['btn_urgency_3'][0]}

                markup = make_keyboard_inline(2, **kbd_urgency)

                title_msg = await bot.send_message(chat_id=call.message.chat.id,
                                                   text=Config.MSG_SELECT_UGRENCY,
                                                   reply_markup=markup)

                msgid_dict[call.message.chat.id].append(title_msg.message_id)

            # Select urgency
            elif call.data.startswith('btn_urgency_'):
                # Set urgency_id in Ticket object
                btn_name = call.data
                urgency_id = Config.KBD_URGENCY[btn_name][1]
                ticket_dict[call.message.chat.id].urgency_id = urgency_id

                # Delete message with inline keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                # send message
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='Срочность: ' + Config.KBD_URGENCY[btn_name][0])

                # Display message about define problem
                await bot.send_message(chat_id=call.message.chat.id,
                                       text=Config.MSG_DEFINE_PROBLEM,
                                       reply_markup=None)
            else:
                pass
    except Exception as err:
        logger.warning('callback_inline(%s) - some errors: %s and ticket was not created',
                       str(call.message.chat.id), repr(err))
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=Config.MSG_ERROR_ATTENTION,
                                    reply_markup=None)
        await stop(call.message)
    finally:
        logger.info("the function callback_inline(call) is done for the id %s", str(call.message.chat.id))


if __name__ == "__main__":
    # run bot
    executor.start_polling(dp, skip_updates=True)
