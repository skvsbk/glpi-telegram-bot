from .serializer import serialize_ticket
from app.utils import user_dict, tickets_for_close_dict, ticket_for_approve, tickets_for_comment_dict
from app.utils import ticket_for_comment
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
        for ticket in tickets.items():
            tickets_for_comment_dict[chat_id] = []
            msg_item = serialize_ticket(ticket)
            await bot.send_message(chat_id=chat_id,
                                   text=msg_item,
                                   parse_mode='html')
            # Fill the dict for further make inline keyboard and make close ticket
            tickets_for_comment_dict[chat_id].append(ticket[0])

        # Select action
        await select_action(chat_id, Config.KBD_COMMENT_TICKET, Config.MSG_SELECT_ACTION, True)


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
        tickets_for_close_dict[chat_id] = []
        for ticket in tickets.items():
            msg_item = serialize_ticket(ticket)
            await bot.send_message(chat_id=chat_id,
                                   text=msg_item,
                                   parse_mode='html')
            # Fill the dict for further make inline keyboard and make close ticket
            tickets_for_close_dict[chat_id].append(ticket[0])

        # Select action fir close tickets
        await select_action(chat_id, Config.KBD_CLOSE_TICKET, Config.MSG_SELECT_ACTION, True)


async def btn_close(chat_id, btn_name):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    ticket_id = btn_name.replace('btn_close_', '')
    ticket_for_approve[chat_id] = ticket_id
    # ticket_for_comment[chat_id] = ''
    await select_action(chat_id, Config.KBD_APPROVE_REJECT, Config.MSG_SELECT_ACTION, True)


async def btn_comment(chat_id, btn_name):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    ticket_id = btn_name.replace('btn_comment_', '')
    ticket_for_comment[chat_id] = ticket_id
    # ticket_for_approve[chat_id] = ''
    # await select_action(chat_id, Config.KBD_APPROVE_REJECT, Config.MSG_SELECT_ACTION, True)
    await bot.send_message(chat_id=chat_id, text=Config.MSG_LEAVE_COMMENT)


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


async def leave_comment(chat_id, comment):
    ticket_id = ticket_for_comment.get(chat_id)
    # Do comment
    status = glpiapi.leave_ticket_comment(chat_id, ticket_id, comment)
    # Check comment
    # status = glpiapi.check_ticket_status(chat_id, ticket_id)
    if status is not None and status.status_code in (200, 201):
        msg = f'Коментарий для заявки №{ticket_id} сохранен'
    else:
        msg = f'Коментарий для заявки №{ticket_id} не сохранен, попробуйте сделать это с помощью компьютера'
    await bot.send_message(chat_id=chat_id, text=msg)
    # Return to choice
    await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)


async def close_tickets(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Make inline keyboard with tickets number
    kbd_tickets = {}
    for item in tickets_for_close_dict[chat_id]:
        kbd_tickets.update({f'btn_close_{item}': str(item)})
    kbd_tickets.update({f'btn_tickets_exit': "Назад"})
    # Select action fir close tickets
    await select_action(chat_id, kbd_tickets, Config.MSG_SELECT_FOR_CLOSE, True)


async def comment_tickets(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Make inline keyboard with tickets number
    kbd_tickets = {}
    for item in tickets_for_comment_dict[chat_id]:
        kbd_tickets.update({f'btn_comment_{item}': str(item)})
    kbd_tickets.update({f'btn_tickets_exit': "Назад"})
    # Select action fir close tickets
    await select_action(chat_id, kbd_tickets, Config.MSG_SELECT_FOR_COMMENT, True)
