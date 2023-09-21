from app.utils import user_dict, close_tickets_dict, ticket_for_approve
from app.utils import glpidb, glpiapi
from .utilities import delete_inline_keyboard, select_action
from app.config import Config
from app import bot


async def role_init(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id, text=Config.MSG_INIT_ROLE)
    # Make 2 btn: "in progress" and "solved"
    await select_action(chat_id, Config.KBD_STATUS, Config.MSG_SELECT_STATUS, True)


async def status_atwork(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id, text=Config.MSG_INIT_STATUS_1)
    query_string = glpidb.query_tickets_init_atwork(user_dict[chat_id].id)
    tickets = glpidb.get_tickets(query_string)
    if tickets == {}:
        await bot.send_message(chat_id=chat_id, text=Config.MSG_INIT_EMPTY_WORK_1)
        # Select action
        await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
    else:
        for item in tickets.items():
            msg_item = (f"<b>Заявка № {item[0]}</b>\n"
                        f"Дата: {item[1]['date']}\n"
                        f"Статус: {item[1]['status']}\n"
                        f"Тема: {item[1]['name']}\n"
                        f"Описание: {item[1]['content']}\n"
                        f"Исполнитель: {item[1]['user_name']}")
            await bot.send_message(chat_id=chat_id,
                                   text=msg_item,
                                   parse_mode='html')

        # Select action
        await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)


async def status_solved(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id, text=Config.MSG_INIT_STATUS_2)

    query_string = glpidb.query_solved_tickets(user_dict[chat_id].id)
    tickets = glpidb.get_tickets(query_string)
    if tickets == {}:
        await bot.send_message(chat_id=chat_id, text=Config.MSG_INIT_EMPTY_WORK_2)
        # Select action
        await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
    else:
        close_tickets_dict[chat_id] = []
        for item in tickets.items():
            msg_item = (f"<b>Заявка № {item[0]}</b>\n"
                        f"Дата: {item[1]['date']}\n"
                        f"Статус: {item[1]['status']}\n"
                        f"Тема: {item[1]['name']}\n"
                        f"Описание: {item[1]['content']}\n"
                        f"Исполнитель: {item[1]['user_name']}")
            await bot.send_message(chat_id=chat_id,
                                   text=msg_item,
                                   parse_mode='html')
            # Fill the dict for further make inline keyboard and make close ticket
            close_tickets_dict[chat_id].append(item[0])

        # Select action fir close tickets
        await select_action(chat_id, Config.KBD_CLOSE_TICKET, Config.MSG_SELECT_ACTION, True)


async def btn_close(chat_id, btn_name):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    ticket_id = btn_name.replace('btn_close_', '')
    ticket_for_approve[chat_id] = ticket_id
    await select_action(chat_id, Config.KBD_APPROVE_REJECT, Config.MSG_SELECT_ACTION, True)


async def btn_approve(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    ticket_id = ticket_for_approve.get(chat_id)
    # Approve solution
    glpiapi.approve_ticket(chat_id, ticket_id)
    # Check status
    status = glpiapi.check_ticket_status(chat_id, ticket_id)
    if status == 6:
        msg = f'Решение по заявке № {ticket_id} утверждено'
    else:
        msg = f'Решение по заявке№ {ticket_id} не принято, попробуйте сделать это с помощью компьютера'
    await bot.send_message(chat_id=chat_id, text=msg)
    # Return to choice
    await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)


async def btn_reject(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_REJECT_REASON)


async def reject_ticket_whith_msg(chat_id, msg_reject):
    ticket_id = ticket_for_approve.get(chat_id)
    # Do refuse
    glpiapi.refuse_ticket(chat_id, ticket_id, msg_reject)
    # Check status
    status = glpiapi.check_ticket_status(chat_id, ticket_id)
    if status == 2:
        msg = f'Решение по заявке № {ticket_id} отклонено'
    else:
        msg = f'Решение по заявке № {ticket_id} не принято, попробуйте сделать это с помощью компьютера'
    await bot.send_message(chat_id=chat_id, text=msg)
    # Return to choice
    await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)


async def close_tickets(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Make inline keyboard with tickets number
    kbd_tickets = {}
    for item in close_tickets_dict[chat_id]:
        kbd_tickets.update({f'btn_close_{item}': str(item)})
    kbd_tickets.update({f'btn_tickets_exit': "Назад"})
    # Select action fir close tickets
    await select_action(chat_id, kbd_tickets, Config.MSG_SELECT_FOR_CLOSE, True)
