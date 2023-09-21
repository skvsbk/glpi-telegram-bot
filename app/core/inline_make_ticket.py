from app.utils import user_dict, glpi_dict, ticket_dict
from app.utils import glpidb
from .utilities import delete_inline_keyboard, select_action
from app.config import Config
from app import bot


async def theme_equipment(chat_id):
    # save choice to dict or object Ticket
    ticket_dict[chat_id].name = Config.BTN_THEME_EQIPMENT
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # send message
    await bot.send_message(chat_id=chat_id,
                           text='Тема: ' + ticket_dict[chat_id].name)
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_ENTER_NAME_EQUIPMENT)


async def theme_room(chat_id):
    # save choice to dict or object Ticket
    ticket_dict[chat_id].name = Config.BTN_THEME_ROOM
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # send message
    await bot.send_message(chat_id=chat_id,
                           text='Тема: ' + ticket_dict[chat_id].name)
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_ENTER_NAME_ROOM)


async def btn_add(chat_id, message_id):
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=Config.MSG_DEFINE_PROBLEM_PHOTO,
                                reply_markup=None)


async def btn_send(chat_id):
    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_chat_action(chat_id=chat_id, action='upload_document')
    # send ticket
    glpi_dict[chat_id].ticket = ticket_dict[chat_id]
    ticket_id = glpi_dict[chat_id].create_ticket()
    ticket_dict[chat_id].id = ticket_id
    # upload files/photos/videos to glpi
    for filename in ticket_dict[chat_id].attachment:
        # print(filename)
        doc_id = glpi_dict[chat_id].upload_doc(Config.FILE_PATH, filename)
        if doc_id is not None:
            # update table glpi_documents_items
            glpidb.update_doc_item(doc_id, ticket_id, user_dict[chat_id].id)
    if ticket_id is not None:
        await bot.send_message(chat_id=chat_id,
                               text="Заявка №" + str(ticket_id) + " успешно оформлена",
                               reply_markup=None)
    else:
        await bot.send_message(chat_id=chat_id,
                               text=Config.MSG_ERROR_SEND,
                               reply_markup=None)


async def cancel_or_exit(chat_id, message_id):
    if ticket_dict[chat_id].name == '':
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    else:
        await delete_inline_keyboard(chat_id)
        await bot.send_message(chat_id=chat_id,
                               text=Config.MSG_CANCEL,
                               reply_markup=None)


async def btn_category(chat_id, btn_name):
    # Set category_id in Ticket object
    category_id = Config.KBD_CATEGORY[btn_name][1]
    ticket_dict[chat_id].category_id = category_id

    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)

    # send message
    await bot.send_message(chat_id=chat_id,
                           text='Категория: ' + Config.KBD_CATEGORY[btn_name][0])

    # Display urgency
    kbd_urgency = {'btn_urgency_1': Config.KBD_URGENCY['btn_urgency_1'][0],
                   'btn_urgency_2': Config.KBD_URGENCY['btn_urgency_2'][0],
                   'btn_urgency_3': Config.KBD_URGENCY['btn_urgency_3'][0]}

    await select_action(chat_id, kbd_urgency, Config.MSG_SELECT_UGRENCY, True)


async def btn_urgency(chat_id, btn_name):
    # Set urgency_id in Ticket object
    urgency_id = Config.KBD_URGENCY[btn_name][1]
    ticket_dict[chat_id].urgency_id = urgency_id

    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)

    # send message
    await bot.send_message(chat_id=chat_id,
                           text='Срочность: ' + Config.KBD_URGENCY[btn_name][0])

    # Display message about define problem
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_DEFINE_PROBLEM)
