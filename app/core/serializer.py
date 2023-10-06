from app.config import Config


def serialize_ticket(ticket):
    message = (f"<b>Заявка № {ticket[0]}</b>\n"
               f"Дата: {ticket[1]['date']}\n"
               f"Статус: {ticket[1]['status']}\n"
               f"Тема: {ticket[1]['name']}\n"
               f"Описание: {ticket[1]['content']}\n"
               f"Инициатор: {ticket[1]['user_name']}")
    return message


def serialize_project(project):
    message = (f"<b>Kaidzen № {project.get('id')}</b>\n"
               f"Дата: {project.get('date')}\n"
               f"Статус: {Config.PROJECT_STATUS.get(int(project.get('projectstates_id')))}\n" 
               f"Тема: {project.get('name')}\n"
               f"Описание: {project.get('content')}\n")
    return message
