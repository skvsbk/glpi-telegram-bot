from app.config import Config
from app import bot
from app.utils import user_dict, glpi_dict, ticket_dict, msgid_dict
from app.utils import glpidb
from .utils import delete_inline_keyboard, make_keyboard_inline, make_category_keyboard
from .stop import stop

import logging


# logging
logging.basicConfig(level=logging.WARNING, filename='glpibot.log',
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def callback_inline_keyboard(call):
    try:
        if call.message:
            if call.data == 'btn_theme_equipment':
                # save choice to dict or object Ticket
                ticket_dict[call.message.chat.id].name = Config.BTN_THEME_EQIPMENT

                # Delete inlaine keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                # send message
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='Тема: ' + ticket_dict[call.message.chat.id].name)
                await bot.send_message(chat_id=call.message.chat.id,
                                       text=Config.MSG_ENTER_NAME_EQUIPMENT)

            if call.data == 'btn_theme_room':
                # save choice to dict or object Ticket
                ticket_dict[call.message.chat.id].name = Config.BTN_THEME_ROOM

                # Delete inlaine keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                # send message
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='Тема: ' + ticket_dict[call.message.chat.id].name)
                await bot.send_message(chat_id=call.message.chat.id,
                                       text=Config.MSG_ENTER_NAME_ROOM)

            elif call.data == 'btn_add':
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

            elif call.data in ('btn_cancel', 'btn_theme_exit'):
                if ticket_dict[call.message.chat.id].name == '':
                    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                else:
                    await bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id=call.message.message_id,
                                                text=Config.MSG_CANCEL,
                                                reply_markup=None)
                await stop(call.message)

            # Select Help
            elif call.data == 'btn_categ_help':
                # Delete message with inline keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)

                kbd_add_send_cancel = {'btn_understand': Config.BTN_UNDERSTAND}
                markup = make_keyboard_inline(1, **kbd_add_send_cancel)
                title_msg = await bot.send_message(chat_id=call.message.chat.id,
                                                   text=Config.MSG_HELP,
                                                   parse_mode='html',
                                                   reply_markup=markup)
                msgid_dict[call.message.chat.id].append(title_msg.message_id)

            # Select Understand
            elif call.data == 'btn_understand':
                # Delete message with inline keyboard
                await delete_inline_keyboard(bot, msgid_dict, call.message.chat.id)
                # Select category keyboard
                await make_category_keyboard(bot, msgid_dict, call.message)

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
