from app.utils import msg_id_dict
from .utilities import delete_inline_keyboard, make_keyboard_inline, make_category_keyboard, select_action
from app.config import Config
from app import bot


async def action_make(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Select type of ticket
    await select_action(chat_id, Config.KBD_THEME, Config.MSG_SELECT_ACTION, True)


async def action_mytickets(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_MY_TICKETS)
    # Select type of role
    await select_action(chat_id, Config.KBD_ROLE, Config.MSG_SELECT_ROLE, True)


async def btn_help(chat_id):
    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)

    kbd_add_send_cancel = {'btn_understand': Config.BTN_UNDERSTAND}
    markup = make_keyboard_inline(1, **kbd_add_send_cancel)
    title_msg = await bot.send_message(chat_id=chat_id,
                                       text=Config.MSG_HELP,
                                       parse_mode='html',
                                       reply_markup=markup)
    msg_id_dict[chat_id].append(title_msg.message_id)


async def btn_understand(chat_id):
    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)
    # Select category keyboard
    await make_category_keyboard(chat_id)
