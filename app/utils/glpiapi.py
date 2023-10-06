import requests
import json
from datetime import datetime, timedelta
from app.config import Config
from app.utils.glpidb import get_equipment_id, get_location_id
from app.utils import glpi_dict, user_dict


import logging


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


class User:
    def __init__(self, user_id=None, token=None, locations_name=None):
        self.id = user_id
        self.token = token
        self.locations_name = locations_name

    def print_user(self):
        print(f'user_id: {self.id}; user_token: {self.token}')


class Ticket:
    def __init__(self):
        self.id = None
        self.name = ''
        self.content = ''
        self.category_id = None
        self.urgency_id = None
        self.attachment = []
        self.isnew = False

    def print_ticket(self):
        print(f't_id: {self.id}; t_name: {self.name}; t_content: {self.content}; t_attachment: {self.attachment}')


class Project:
    def __init__(self):
        self.id = None
        self.name = ''
        self.content = ''
        self.attachment = []
        self.isnew = False


class GLPI:
    def __init__(self, url=None, user=None, ticket=None, project=None):
        self.url = url
        self.user = user
        self.ticket = ticket
        self.project = project

        # User session initialization
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"user_token {self.user.token}"
        }
        response = requests.get(self.url+"/initSession", headers=headers)
        if response.status_code == 401 or response.status_code == 400:
            self.session = None
            self.header = None
        else:
            self.session = json.loads(response.text).get('session_token')
            self.headers = {"Content-Type": "application/json",
                            "Authorization": "user_token " + self.user.token,
                            "Session-Token": self.session
                            }

    def __del__(self):
        if self.session:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session,
            }
            requests.get(self.url+"/killSession", headers=headers)

    def create_ticket(self):
        if self.ticket.id is None:
            if self.ticket.content == '':
                self.ticket.content = self.ticket.name

            itilcategories_id = self.ticket.category_id
            urgency_id = self.ticket.urgency_id

            time_to_resolve = str(datetime.today().date() + timedelta(5)) + ' 12:00:00'

            msg_dict = {"input": {"name": self.ticket.name,
                                  "content": self.ticket.content,
                                  "time_to_resolve": time_to_resolve,
                                  "itilcategories_id": itilcategories_id,
                                  "type": Config.TYPE,
                                  "requesttypes_id": Config.REQUESTTYPE_ID,
                                  "urgency": urgency_id}
                        }

            equipment_ids = None

            if self.ticket.name.startswith(Config.BTN_THEME_ROOM):
                location_name = self.ticket.name.split()[1]
                location_id = get_location_id(location_name)
                if location_id is not None:
                    msg_dict["input"].update({"locations_id": location_id})
            if self.ticket.name.startswith(Config.BTN_THEME_EQIPMENT):
                equipment_name = self.ticket.name.split()[1]
                equipment_ids = get_equipment_id(equipment_name)
                if equipment_ids is not None and equipment_ids['locations_id']:
                    msg_dict["input"].update({"locations_id": equipment_ids['locations_id']})

            payload = json.dumps(msg_dict).encode('utf-8')
            response = requests.post(self.url+"/Ticket", headers=self.headers, data=payload)
            logger.info(f'{self.url}/Ticket status_code={response.status_code}')

            if response.status_code == 201:
                self.ticket.id = json.loads(response.text).get('id')

                # Assign equipment with ticket
                if self.ticket.name.startswith(Config.BTN_THEME_EQIPMENT) and equipment_ids is not None:
                    url = f'{self.url}/Ticket/{self.ticket.id}/Item_Ticket/'
                    msg_dict = {"input": {"tickets_id": self.ticket.id,
                                          "items_id": equipment_ids['id'],
                                          "itemtype": "Peripheral"}
                                }
                    payload = json.dumps(msg_dict).encode('utf-8')
                    response = requests.post(url, headers=self.headers, data=payload)
                    logger.info(f'{url} status_code={response.status_code}')

        return self.ticket.id

    def create_project(self):
        if self.project.id is None:
            if self.project.content == '':
                self.project.content = self.project.name

            msg_dict = {"input": {"name": self.project.name,
                                  "content": self.project.content,
                                  "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  "users_id": self.user.id,
                                  "priority": 3,
                                  "projectstates_id": 0
                                  }
                        }

            payload = json.dumps(msg_dict).encode('utf-8')
            response = requests.post(self.url+"/Project", headers=self.headers, data=payload)
            logger.info(f'{self.url}/Project status_code={response.status_code}')

            if response.status_code == 201:
                self.project.id = json.loads(response.text).get('id')

        if self.project.id:
            msg_dict = {"input": {"projects_id": self.project.id,
                                  "itemtype": "User",
                                  "items_id": Config.PROJECT_MANAGER_ID
                                  }
                        }

            payload = json.dumps(msg_dict).encode('utf-8')
            response = requests.post(f"{self.url}/Project/{self.project.id}/ProjectTeam",
                                     headers=self.headers, data=payload)
            logger.info(f'{self.url}/Project{self.project.id}/ProjectTeam status_code={response.status_code}')

        return self.project.id

    def upload_doc(self, file_path, filename, doc_name):
        doc_id = None
        headers = {'Session-Token': self.session}
        files = {'uploadManifest': (None, '{"input": {"name": "' + doc_name +
                                    ' (tb)", "_filename": ["' + filename + '"]}}', 'application/json'),
                 'filename[0]': (filename, open(file_path + '/' + filename, "rb")), }

        response = requests.post(self.url+"/Document", headers=headers, files=files)

        if response.status_code in range(200, 300):
            doc_id = response.json().get('id')

        # Link doc with Project
        if doc_id is not None:
            if self.ticket is not None:
                item_id = self.ticket.id
                item_type = "Ticket"
            if self.project is not None:
                item_id = self.project.id
                item_type = "Project"

            msg_dict = {"input": {"documents_id": doc_id,
                                  "items_id": item_id,
                                  "itemtype": item_type,
                                  "users_id": self.user.id,
                                  "is_recursive": 1,
                                  }
                        }
            payload = json.dumps(msg_dict).encode('utf-8')
            response = requests.post(f"{self.url}/Document/{doc_id}/Document_Item", headers=self.headers, data=payload)
        if response:
            logger.info(f'{self.url} status_code={response.status_code}')
            if response.status_code >= 400:
                logger.warning(f'{self.url} error = {response.text}')


def api_request(headers: dict, url: str, payload, request_type: str):
    data = json.dumps(payload).encode('utf-8')

    response = None

    if request_type == 'post':
        response = requests.post(url, headers=headers, data=data)
    if request_type == 'put':
        response = requests.put(url, headers=headers, data=data)

    if response:
        logger.info(f'{url} status_code={response.status_code}')
        if response.status_code >= 400:
            logger.warning(f'{url} error = {response.text}')

    return response


def solve_ticket(chat_id, ticket_id):
    headers = glpi_dict[chat_id].headers
    msg_dict = {"input": {"items_id": ticket_id,
                          "content": Config.MSG_SOLUTION,
                          "users_id": glpi_dict[chat_id].user.id,
                          "solutiontypes_id": 0,
                          "itemtype": "Ticket",
                          "status": 5,
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    api_request(headers, f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILSolution', payload, 'post')


def approve_ticket(chat_id, ticket_id):
    headers = glpi_dict[chat_id].headers

    # Get id of last solution
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILSolution'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        solution_id = json.loads(response.content)[-1]['id']
    else:
        return

    request_list = []

    # POST comment approval
    msg_dict = {"input": {"itemtype": "Ticket",
                          "items_id": ticket_id,
                          "users_id": glpi_dict[chat_id].user.id,
                          "content": Config.MSG_APPROVAL,
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    request_list.append((url, payload, 'post'))

    # PUT to last solution
    msg_dict = {"input": {"items_id": ticket_id,
                          "users_id_approval": glpi_dict[chat_id].user.id,
                          "solutiontypes_id": 1,
                          "itemtype": "Ticket",
                          "status": 3
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILSolution/{solution_id}'
    request_list.append((url, payload, 'put'))

    # PUT status Closed for Ticket
    payload = {"input": {"id": ticket_id,
                         "status": 6}
               }
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}'
    request_list.append((url, payload, 'put'))

    for item in request_list:
        api_request(headers, item[0], item[1], item[2])


def refuse_ticket(chat_id, ticket_id, msg_reason):
    headers = glpi_dict[chat_id].headers

    # Get id of last solution
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILSolution'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        solution_id = json.loads(response.content)[-1]['id']
    else:
        return

    request_list = []

    # POST comment approval
    msg_dict = {"input": {"itemtype": "Ticket",
                          "items_id": ticket_id,
                          "users_id": glpi_dict[chat_id].user.id,
                          "content": msg_reason,
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    request_list.append((url, payload, 'post'))

    # PUT to last solution
    msg_dict = {"input": {"items_id": ticket_id,
                          "users_id": 0,
                          "users_id_approval": glpi_dict[chat_id].user.id,
                          "solutiontypes_id": 0,
                          "itemtype": "Ticket",
                          "status": 4,
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILSolution/{solution_id}'
    request_list.append((url, payload, 'put'))

    # PUT status Closed for Ticket
    ticket_dict = {"input": {"id": ticket_id,
                             "status": 2}
                   }
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}'
    request_list.append((url, ticket_dict, 'put'))

    for item in request_list:
        api_request(headers, item[0], item[1], item[2])


def check_ticket_status(chat_id, ticket_id):
    headers = glpi_dict[chat_id].headers

    # Get id of last solution
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)['status']
    else:
        return 0


def leave_ticket_comment(chat_id, ticket_id, comment):
    headers = glpi_dict[chat_id].headers

    # POST comment
    msg_dict = {"input": {"itemtype": "Ticket",
                          "items_id": ticket_id,
                          "users_id": glpi_dict[chat_id].user.id,
                          "content": comment,
                          }
                }
    payload = json.dumps(msg_dict).encode('utf-8')
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    return api_request(headers, url, payload, 'post')


def get_user_projects(chat_id):
    headers = glpi_dict[chat_id].headers
    user_id = user_dict[chat_id].id
    url = f'{Config.URL_GLPI}/User/{user_id}/Project'
    response = requests.get(url, headers=headers)

    if response:
        logger.info(f'{url} status_code={response.status_code}')
        if response.status_code >= 400:
            logger.warning(f'{url} error = {response.text}')
            return
        projects = response.content
        return json.loads(projects)


if __name__ == '__main__':
    print('glpiapi module')
