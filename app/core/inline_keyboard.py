from app.config import Config
from app import bot
from .utilities import delete_inline_keyboard, select_action
from .stop import stop_bot
from . import inline_common, inline_tickets_init, inline_make_ticket, inline_tickets_handler

import logging


# logging
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


async def callback_inline_keyboard(call):
    try:
        if call.message:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            if call.data == 'bnt_action_make':
                await inline_common.action_make(chat_id)

            if call.data == 'bnt_action_mytickets':
                await inline_common.action_mytickets(chat_id)

            if call.data == 'btn_role_init':
                await inline_tickets_init.role_init(chat_id)

            if call.data == 'btn_role_handler':
                await inline_tickets_handler.role_handler(chat_id)

            if call.data == 'btn_handler_solve':
                await inline_tickets_handler.solve_tickets(chat_id)

            elif call.data.startswith('btn_solve_'):
                await inline_tickets_handler.btn_solve(chat_id, call.data)

            elif call.data.startswith('btn_close_'):
                await inline_tickets_init.btn_close(chat_id, call.data)

            if call.data == 'btn_init_status_solved':
                await inline_tickets_init.status_solved(chat_id)

            if call.data == 'btn_init_close':
                await inline_tickets_init.close_tickets(chat_id)

            if call.data == 'btn_init_status_atwork':
                await inline_tickets_init.status_atwork(chat_id)

            if call.data == 'btn_init_approve':
                await inline_tickets_init.btn_approve(chat_id)

            if call.data == 'btn_init_reject':
                await inline_tickets_init.btn_reject(chat_id)

            if call.data == 'btn_theme_equipment':
                await inline_make_ticket.theme_equipment(chat_id)

            if call.data == 'btn_theme_room':
                await inline_make_ticket.theme_room(chat_id)

            elif call.data == 'btn_add':
                await inline_make_ticket.btn_add(chat_id, message_id)

            elif call.data == 'btn_send':
                await inline_make_ticket.btn_send(chat_id)
                await stop_bot(call.message)

            elif call.data in ('btn_cancel', 'btn_action_exit'):
                await inline_make_ticket.cancel_or_exit(chat_id, message_id)
                await stop_bot(call.message)

            if call.data == 'btn_tickets_exit':
                # Delete inline keyboard
                await delete_inline_keyboard(chat_id)
                # Select action
                await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)

            # Select Help
            elif call.data == 'btn_categ_help':
                await inline_common.btn_help(chat_id)

            # Select Understand
            elif call.data == 'btn_understand':
                await inline_common.btn_understand(chat_id)

            # Select category
            elif call.data.startswith('btn_category_'):
                await inline_make_ticket.btn_category(chat_id, call.data)

            # Select urgency
            elif call.data.startswith('btn_urgency_'):
                await inline_make_ticket.btn_urgency(chat_id, call.data)

            else:
                pass
    except Exception as err:
        logger.warning('callback_inline(%s) - some errors: %s and ticket was not created',
                       str(call.message.chat.id), repr(err))
        await bot.send_message(chat_id=call.message.chat.id,
                               text=Config.MSG_ERROR_ATTENTION,
                               reply_markup=None)
        await stop_bot(call.message)
    finally:
        logger.info("the function callback_inline() is done for the id %s", str(call.message.chat.id))
