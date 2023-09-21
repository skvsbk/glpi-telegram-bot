from aiogram import types
from app.config import Config
from app import bot
from app.utils import msgid_dict


def make_keyboard_inline(row_width, **buttons):
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    key_list = []
    for callback_data, button_name in buttons.items():
        key_list.append(types.InlineKeyboardButton(button_name, callback_data=callback_data))
    args = (i for i in key_list)
    return markup.add(*args)


async def delete_inline_keyboard(chat_id):
    msgid_dict_lenghth = len(msgid_dict[chat_id])
    if msgid_dict_lenghth > 0:
        for i in range(msgid_dict_lenghth):
            del_msg_id = msgid_dict[chat_id].pop()
            await bot.delete_message(chat_id=chat_id, message_id=del_msg_id)


async def select_action(chat_id, kbd_action, msg_action, add_msg_id=True):
    markup = make_keyboard_inline(2, **kbd_action)
    title_msg = await bot.send_message(chat_id=chat_id,
                                       text=msg_action,
                                       parse_mode='html',
                                       reply_markup=markup)
    if add_msg_id:
        msgid_dict[chat_id].append(title_msg.message_id)


async def make_category_keyboard(chat_id):
    kbd_category = {'btn_categ_help': Config.KBD_CATEGORY['btn_categ_help'][0],
                    'btn_category_1': Config.KBD_CATEGORY['btn_category_1'][0],
                    'btn_category_2': Config.KBD_CATEGORY['btn_category_2'][0],
                    'btn_category_3': Config.KBD_CATEGORY['btn_category_3'][0],
                    'btn_category_4': Config.KBD_CATEGORY['btn_category_4'][0],
                    'btn_category_5': Config.KBD_CATEGORY['btn_category_5'][0],
                    'btn_category_6': Config.KBD_CATEGORY['btn_category_6'][0],
                    'btn_category_7': Config.KBD_CATEGORY['btn_category_7'][0]}
    await select_action(chat_id, kbd_category, Config.MSG_SELECT_TYPE, add_msg_id=True)
