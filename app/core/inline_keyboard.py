from app.config import Config
from app import bot
from .stop import stop_bot
from . import inline_common, inline_tickets_init, inline_make_ticket, inline_tickets_executor, inline_kaidzen

import logging


# logging
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

action_for_fullname = {'bnt_action_make': inline_common.action_make,
                       'bnt_action_mytickets': inline_common.action_mytickets,
                       'bnt_action_kaidzen': inline_kaidzen.action_kaidzen,
                       'btn_action_exit': inline_make_ticket.cancel_or_exit_ticket,

                       'btn_role_init': inline_tickets_init.role_init,
                       'btn_role_handler': inline_tickets_executor.role_executor,

                       'btn_executor_solve': inline_tickets_executor.solve_tickets,

                       'btn_init_status_solved': inline_tickets_init.status_solved,
                       'btn_init_close': inline_tickets_init.close_tickets,
                       'btn_init_status_atwork': inline_tickets_init.status_atwork,
                       'btn_init_comment': inline_tickets_init.comment_tickets,
                       'btn_init_approve': inline_tickets_init.btn_approve,
                       'btn_init_reject': inline_tickets_init.btn_reject,

                       'btn_theme_equipment': inline_make_ticket.theme_equipment,
                       'btn_theme_room': inline_make_ticket.theme_room,

                       'btn_kaidzen_my_offers': inline_kaidzen.kaidzen_my_offers,
                       'btn_kaidzen_make': inline_kaidzen.kaidzen_add_name,
                       'btn_add_kaidzen': inline_kaidzen.btn_add_kaidzen,

                       'btn_category_help': inline_common.btn_help,
                       'btn_understand': inline_common.btn_understand,
                       'btn_backward': inline_common.btn_backward,
                       'btn_cancel_ticket': inline_make_ticket.cancel_or_exit_ticket,

                       'btn_send_ticket': inline_make_ticket.btn_send_ticket,
                       'btn_send_kaidzen': inline_kaidzen.btn_send_kaidzen
                       }

part_names = ('btn_solve_', 'btn_close_', 'btn_comment_', 'btn_category_', 'btn_urgency_')

action_for_partname = {'btn_solve_': inline_tickets_executor.btn_solve,
                       'btn_close_': inline_tickets_init.btn_close,
                       'btn_comment_': inline_tickets_init.btn_comment,
                       'btn_category_': inline_make_ticket.btn_category,
                       'btn_urgency_': inline_make_ticket.btn_urgency,
                       }


def get_partname(name: str):
    """
    for dynamically created buttons
    """
    for item in part_names:
        if name.startswith(item):
            return item
    return None


async def callback_inline_keyboard(call):
    try:
        if call.message:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            part_name = get_partname(call.data)
            if part_name is not None:
                await action_for_partname.get(part_name)(chat_id, call.data)

            if call.data == 'btn_append_ticket':
                await inline_make_ticket.btn_add_ticket(chat_id, message_id)

            action = action_for_fullname.get(call.data)
            if action is not None:
                await action(chat_id)

    except Exception as err:
        logger.warning('callback_inline(%s) - some errors: %s and ticket was not created',
                       str(call.message.chat.id), repr(err))
        await bot.send_message(chat_id=call.message.chat.id,
                               text=Config.MSG_ERROR_ATTENTION,
                               reply_markup=None)
        await stop_bot(call.message.chat.id)
    finally:
        logger.info("the function callback_inline() is done for the id %s", str(call.message.chat.id))
