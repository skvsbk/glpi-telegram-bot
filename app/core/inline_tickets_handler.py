from app.utils import user_dict, tickets_for_solve_dict
from app.utils import glpidb, glpiapi
from .utilities import delete_inline_keyboard, select_action
from app.config import Config
from app import bot


async def role_handler(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id, text=Config.MSG_HANDLER_ROLE)
    query_string = glpidb.query_tickets_executer_atwork(user_dict[chat_id].id)
    tickets = glpidb.get_tickets(query_string)
    if tickets == {}:
        await bot.send_message(chat_id=chat_id, text=Config.MSG_HANDLER_EMPTY_ROLE)
        # Select action
        await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
    else:
        tickets_for_solve_dict[chat_id] = []
        for item in tickets.items():
            msg_item = (f"<b>Заявка № {item[0]}</b>\n"
                        f"Дата: {item[1]['date']}\n"
                        f"Статус: {item[1]['status']}\n"
                        f"Тема: {item[1]['name']}\n"
                        f"Описание: {item[1]['content']}\n"
                        f"Инициатор: {item[1]['user_name']}")
            await bot.send_message(chat_id=chat_id,
                                   text=msg_item,
                                   parse_mode='html')
            # Fill the dict for further make inline keyboard and make solve ticket
            tickets_for_solve_dict[chat_id].append(item[0])

        # Select action for solve tickets
        await select_action(chat_id, Config.KBD_SOLVE_TICKET, Config.MSG_SELECT_ACTION, True)


async def solve_tickets(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Make inline keyboard with tickets number
    kbd_tickets = {}
    for item in tickets_for_solve_dict[chat_id]:
        kbd_tickets.update({f'btn_solve_{item}': str(item)})
    kbd_tickets.update({f'btn_tickets_exit': "Назад"})
    # Select action fir solve tickets
    await select_action(chat_id, kbd_tickets, Config.MSG_SELECT_FOR_SOLVE, True)


async def btn_solve(chat_id, btn_name):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    ticket_id = btn_name.replace('btn_solve_', '')
    # Sovle ticket
    glpiapi.solve_ticket(chat_id, ticket_id)

    # Check status
    status = glpiapi.check_ticket_status(chat_id, ticket_id)
    if status == 5:
        msg = f'Заявка № {ticket_id} решена'
    else:
        msg = f'Заявка № {ticket_id} не решена, попробуйте сделать это с помощью компьютера'
    await bot.send_message(chat_id=chat_id,
                           text=msg)
    # Return to choice
    await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)
