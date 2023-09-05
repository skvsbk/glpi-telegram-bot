import os
from dotenv import load_dotenv


class Config:
    load_dotenv('././.env')

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    URL_GLPI = os.getenv('URL_GLPI')
    FILE_PATH = './app/images'

    # Database usage
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')

    # Buttons name
    BTN_SEND_NUMBER = "Отправить номер"
    BTN_THEME_EXIT = "Выход"
    BTN_THEME_EQIPMENT = "Оборудование"
    BTN_THEME_ROOM = "Помещение"
    BTN_ADD = "Дополнить"
    BTN_SEND_TICKET = "Отправить в ОГИ"
    BTN_CANCEL = "Отменить"
    BTN_UNDERSTAND = "Всё понятно"

    # Messages text
    MSG_AUTH_ATTENTION = f"Для авторизации необходим номер телефона.\n" + \
                         "Нажмите <u>кнопку</u> <b>Отправить номер</b> (↓ внизу ↓).\n\n" + \
                         "Отправляя свой номер телефона, Вы даете согласие на обработку персональных данных " + \
                         "(ФИО, номер телефона) в целях работы с информационной системой."
    MSG_WELLCOME = "Добро пожаловать."
    MSG_INTRODUCTION = "Я - бот компании Активный компонент. Со мной можно получить помощь ОГИ."
    MSG_SELECT_TITLE = "Выберите тему обращения:"
    MSG_ENTER_NAME_EQUIPMENT = "Введите номер оборудования (Р-1.038):"
    MSG_ENTER_NAME_ROOM = "Введите номер помещения (1.206):"
    MSG_SELECT_TYPE = "Выберите категорию работ:"
    MSG_SELECT_UGRENCY = "Выберите срочность:"
    MSG_DEFINE_PROBLEM = "Опишите проблему:."
    MSG_CAN_ADD = "Вы можете дополнить заявку фото, видео или текстовым сообщением либо завершить:"
    MSG_GOODBY = "До новых встреч."

    MSG_HELP = "<b>Замена</b>: замена воды контура охлаждения ВВН (водокольцевой вакуумный насос)\n" +\
               "<b>Вкл/Выкл</b>: Необходимость включения либо выключения щитов управления, панелей, оборудования в " + \
               "ведении ОГИ, вне доступа технологов \n" + \
               "<b>КИПиА</b>: Работы с ЩУГ, термопарами, уровнемерами, манометрами, пультами управления, " + \
               "контроллерами)\n" + \
               "<b>Сварка</b>: Сварочные работы\n" + \
               "<b>Сборка/Разборка</b>: Сборка/разборка оборудования, например друк-фильтр, сборник, мерник, " +\
               "мельница и т.д.,  линии трубопроводов\n" + \
               "<b>Термостат</b>: Все проблемы с термостатами\n" + \
               "<b>АХО</b>: Мелкие хозяйственные поручения (повесить зеркало, засиликонить раковину, собрать шкаф, " +\
               "поменять доводчик)\n"

    # Error messages
    MSG_AUTH_ERROR = "К сожалению, мы не смоги Вас авторизовать. Обратитесь в IT-отдел."
    MSG_KEYBOARD_ATTENTION = "Используйте, пожалуйста, кнопки."

    MSG_ERROR_ATTENTION = "Что-то пошло не так. Возможно необходимо авторизоваться, нажав /start. " + \
                          "Обратитесь в IT-отдел."
    MSG_ERROR_SEND = "Заявка не создана. Обратитесь в ИТ-отдел."
    MSG_CANCEL = "Заявка отменена."

    # Keyboards
    KBD_CATEGORY = {"btn_categ_help": ["Помощь", 0],
                    "btn_category_1": ["Замена", 6],
                    "btn_category_2": ["Вкл/Выкл", 8],
                    "btn_category_3": ["КИПиА", 14],
                    "btn_category_4": ["Сварка", 12],
                    "btn_category_5": ["Сборка/Разборка", 5],
                    "btn_category_6": ["Термостат", 15],
                    "btn_category_7": ["АХО", 13]
                    }

    KBD_URGENCY = {"btn_urgency_1": ["Обычная", 3],
                   "btn_urgency_2": ["Высокая", 4],
                   "btn_urgency_3": ["Очень высокая", 5]}

    # Create ticket by API
    # TelegramBot = 8
    REQUESTTYPE_ID = "8"
    # Incident = 1
    TYPE = "1"
