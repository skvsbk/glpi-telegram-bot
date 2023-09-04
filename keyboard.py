# from aiogram import types
from aiogram import types
from config import Config


def make_keyboard_inline(row_width, **bottons):
    """
    Make inline keyboard
    :param row_width: number of row appears
    :param bottons: callback_data="botton_name"
    :return: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    key_list = []
    for callback_data, botton_name in bottons.items():
        key_list.append(types.InlineKeyboardButton(botton_name, callback_data=callback_data))
    args = (i for i in key_list)
    return markup.add(*args)


async def delete_inline_keyboard(bot, msgid_dict, chat_id):
    """
    Delete message with inline keyboard
    """
    if len(msgid_dict[chat_id]) > 0:
        for i in range(len(msgid_dict[chat_id])):
            del_msg_id = msgid_dict[chat_id].pop()
            await bot.delete_message(chat_id=chat_id, message_id=del_msg_id)


async def select_ticket_title(bot, msgid_dict, message, add_msg_id=True):
    """
    Select title and get message.chat.id
    """
    kbd_title = {'btn_theme_room': Config.BTN_THEME_ROOM,
                 'btn_theme_equipment': Config.BTN_THEME_EQIPMENT,
                 'btn_theme_exit': Config.BTN_THEME_EXIT}
    markup = make_keyboard_inline(2, **kbd_title)
    title_msg = await bot.send_message(chat_id=message.chat.id,
                                       text=Config.MSG_SELECT_TITLE,
                                       reply_markup=markup)
    if add_msg_id:
        msgid_dict[message.chat.id].append(title_msg.message_id)
