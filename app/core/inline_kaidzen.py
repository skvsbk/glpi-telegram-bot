from .serializer import serialize_project
from app.utils import project_dict, glpi_dict
from .utilities import delete_inline_keyboard, select_action
from app.utils import glpiapi
from app.config import Config
from app import bot


async def action_kaidzen(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Select type of ticket
    await select_action(chat_id, Config.KBD_KAIDZEN, Config.MSG_SELECT_ACTION, True)


async def kaidzen_add_name(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    # Init Project for fill some name and description
    project_dict[chat_id].isnew = True

    await bot.send_message(chat_id=chat_id,
                           text="Введите короткое наименование улучшения:",
                           reply_markup=None)


async def kaidzen_my_offers(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)
    projects = glpiapi.get_user_projects(chat_id)
    for project in projects:
        msg_item = serialize_project(project)
        await bot.send_message(chat_id=chat_id,
                               text=msg_item,
                               parse_mode='html')
    await select_action(chat_id, Config.KBD_ACTION, Config.MSG_SELECT_ACTION, True)


async def btn_add_kaidzen(chat_id):
    # Delete inline keyboard
    await delete_inline_keyboard(chat_id)

    await bot.send_message(chat_id=chat_id,
                           text=Config.MSG_DEFINE_PROBLEM_PHOTO,
                           reply_markup=None)


async def btn_send_kaidzen(chat_id):
    # Delete message with inline keyboard
    await delete_inline_keyboard(chat_id)
    await bot.send_chat_action(chat_id=chat_id, action='upload_document')
    # send ticket
    glpi_dict[chat_id].project = project_dict[chat_id]
    project_id = glpi_dict[chat_id].create_project()
    project_dict[chat_id].id = project_id
    # upload files/photos/videos to glpi
    for filename in project_dict[chat_id].attachment:
        doc_name = F"Документ проекта {project_id}"
        glpi_dict[chat_id].upload_doc(Config.FILE_PATH, filename, doc_name)

    if project_id is not None:
        await bot.send_message(chat_id=chat_id,
                               text="Kaidzen №" + str(project_id) + " успешно оформлен",
                               reply_markup=None)
    else:
        await bot.send_message(chat_id=chat_id,
                               text=Config.MSG_ERROR_SEND_KAIDZEN,
                               reply_markup=None)
