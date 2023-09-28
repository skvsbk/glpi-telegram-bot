import os
from dotenv import load_dotenv


class Config:
    load_dotenv('././.env')

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    URL_GLPI = os.getenv('URL_GLPI')
    FILE_PATH = './app/images'

    LOG_FILENAME = './app/log/bot_creation.log'
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s module:%(name)s %(levelname)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "logfile": {
                "formatter": "default",
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_FILENAME,
                "backupCount": 7,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": [
                "logfile",
            ]
        }
    }

    # Database usage
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')

    # Buttons name
    BTN_SEND_NUMBER = "Отправить номер"
    BTN_ADD = "Дополнить"
    BTN_SEND_TICKET = "Отправить в ОГИ"
    BTN_CANCEL = "Отменить"
    BTN_UNDERSTAND = "Всё понятно"
    BTN_THEME_EQIPMENT = "Оборудование"
    BTN_THEME_ROOM = "Помещение"

    # Messages text
    MSG_AUTH_ATTENTION_1 = (f'Отправляя свой номер телефона, Вы даете согласие на обработку персональных '
                            f'данных (ФИО, номер телефона) в целях работы с информационной системой.')

    MSG_AUTH_ATTENTION_2 = (f'Для авторизации необходим номер телефона.\n'
                            f'Нажмите <u>кнопку</u> <b>Отправить номер</b>\n'
                            f'(↓ кнопка внизу ↓)')
    MSG_WELLCOME = "Добро пожаловать."
    MSG_INTRODUCTION = "Я - бот компании Активный компонент. Со мной можно получить помощь ОГИ."

    MSG_SELECT_THEME = "Выберите тему обращения:"
    MSG_SELECT_ACTION = "Выберите дальнейшие действия:"
    MSG_SELECT_TYPE = "Выберите категорию работ:"
    MSG_SELECT_UGRENCY = "Выберите срочность:"
    MSG_SELECT_ROLE = "Выберите <b>свою</b> роль в заявках:"
    MSG_SELECT_STATUS = "Выберите статус заявки:"
    MSG_SELECT_FOR_SOLVE = "Выберите заявку для решения"
    MSG_SELECT_FOR_CLOSE = "Выберите заявку для закрытия"

    MSG_REJECT_REASON = "Опишите причину:"

    MSG_HANDLER_ROLE = "Роль: Исполнитель"
    MSG_HANDLER_EMPTY_ROLE = "Нет заявок, где Вы назначены исполнителем"

    MSG_INIT_ROLE = "Роль: Инициатор"
    MSG_INIT_STATUS_1 = "Статус: Нерешенные"
    MSG_INIT_STATUS_2 = "Статус: Решена"
    MSG_INIT_EMPTY_WORK_1 = "Нерешенных заявок нет"
    MSG_INIT_EMPTY_WORK_2 = "Решенных заявок нет"

    MSG_ENTER_NAME_EQUIPMENT = "Введите номер оборудования (Р-1.038):"
    MSG_ENTER_NAME_ROOM = "Введите номер помещения (1.206):"

    MSG_DEFINE_PROBLEM = "Опишите проблему:"
    MSG_DEFINE_PROBLEM_PHOTO = "Опишите проблему, сделайте фото или видео..."

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
               "поменять доводчик)\n" + \
               "<b>Проверка</b>: Отклонение в работе оборудования, посторонние шумы\n"

    # Error messages
    MSG_AUTH_ERROR = "К сожалению, мы не смоги Вас авторизовать. Обратитесь в IT-отдел."
    MSG_KEYBOARD_ATTENTION = "Используйте, пожалуйста, кнопки."

    MSG_ERROR_ATTENTION = "Что-то пошло не так. Возможно необходимо авторизоваться, нажав /start. " + \
                          "Обратитесь в IT-отдел."
    MSG_ERROR_SEND = "Заявка не создана. Обратитесь в ИТ-отдел."
    MSG_CANCEL = "Заявка отменена."

    # Keyboards
    KBD_CATEGORY = {"btn_category_1": ("Замена", 6),
                    "btn_category_2": ("Вкл/Выкл", 8),
                    "btn_category_3": ("КИПиА", 14),
                    "btn_category_4": ("Сварка", 12),
                    "btn_category_5": ("Сборка/Разборка", 5),
                    "btn_category_6": ("Термостат", 15),
                    "btn_category_7": ("АХО", 13),
                    "btn_category_8": ("Проверка", 4),
                    "btn_categ_help": ("Помощь", 0),
                    }

    KBD_URGENCY = {"btn_urgency_1": ("Обычная", 3),
                   "btn_urgency_2": ("Высокая", 4),
                   "btn_urgency_3": ("Очень высокая", 5)}

    KBD_ACTION = {"bnt_action_make": "Подать заявку",
                  "bnt_action_mytickets": "Мои заявки",
                  "btn_action_exit": "Выход"}

    KBD_THEME = {"btn_theme_room": BTN_THEME_ROOM,
                 "btn_theme_equipment": BTN_THEME_EQIPMENT}

    KBD_ROLE = {"btn_role_init": "Инициатор",
                "btn_role_handler": "Исполнитель"}

    KBD_STATUS = {"btn_init_status_atwork": "В работе",
                  "btn_init_status_solved": "Решена"}

    KBD_CLOSE_TICKET = {'btn_init_close': "Закрыть заявки",
                        'btn_tickets_exit': "Назад"}

    KBD_SOLVE_TICKET = {'btn_handler_solve': "Решить заявки",
                        'btn_tickets_exit': "Назад"}

    KBD_APPROVE_REJECT = {'btn_init_approve': "Утвердить",
                          'btn_init_reject': "Отклонить",
                          'btn_tickets_exit': "Назад"}

    GLPI_STATUS = {1: 'Новый',
                   2: 'В работе (назначена)',
                   3: 'В работе (запланирована)',
                   4: 'Ожидающие',
                   5: 'Решена',
                   6: 'Закрыто'}

    # Create ticket by API
    # TelegramBot = 8
    REQUESTTYPE_ID = "8"
    # Incident = 1
    TYPE = "1"

    MSG_SOLUTION = 'Выполнено, прошу проверить.(by bot)'
    MSG_APPROVAL = 'Решение одобрено.(by bot)'
