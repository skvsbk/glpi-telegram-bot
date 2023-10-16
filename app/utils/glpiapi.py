import requests
import json
from datetime import datetime, timedelta
from app.config import Config
# from app.utils.glpidb import get_equipment_id, get_location_id, get_user_credentials
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

    def __str__(self):
        return f't_id: {self.id}; t_name: {self.name}; t_content: {self.content}; t_attachment: {self.attachment}'


class Project:
    def __init__(self):
        self.id = None
        self.name = ''
        self.content = ''
        self.attachment = []
        self.isnew = False


class GLPI:
    def __init__(self, url=None, user_obj=None, ticket_obj=None, project_obj=None):
        self.url = url
        self.user = user_obj
        self.ticket = ticket_obj
        self.project = project_obj

        self.session = self._get_user_session()
        if self.session is None:
            self.header = None
        else:
            self.headers = {"Content-Type": "application/json",
                            "Authorization": "user_token " + self.user.token,
                            "Session-Token": self.session
                            }

    def _get_user_session(self):
        # User session initialization
        headers = {"Content-Type": "application/json",
                   "Authorization": f"user_token {self.user.token}"
                   }
        url = self.url + "/initSession"
        response = requests.get(url, headers=headers)

        logger.info(f'{url} status_code={response.status_code}')
        if response.status_code >= 400:
            logger.warning(f'{url} error = {response.text}')
            return None
        return response.json().get('session_token')

    def __del__(self):
        if self.session:
            headers = {
                'Content-Type': 'application/json',
                'Session-Token': self.session,
            }
            requests.get(self.url+"/killSession", headers=headers)

    def create_ticket(self):

        if self.ticket.id:
            return None

        if self.ticket.content == '':
            self.ticket.content = self.ticket.name

        time_to_resolve = str(datetime.today().date() + timedelta(5)) + ' 12:00:00'
        search_name = self.ticket.name.split()[1]
        theme = self.ticket.name.split()[0]
        equipment_or_location = self._get_equipment_or_location(search_name, theme)
        payload = {"input": {"name": self.ticket.name,
                             "content": self.ticket.content,
                             "time_to_resolve": time_to_resolve,
                             "itilcategories_id": self.ticket.category_id,
                             "type": Config.TYPE,
                             "requesttypes_id": Config.REQUESTTYPE_ID,
                             "urgency": self.ticket.urgency_id,
                             "locations_id": equipment_or_location.get('locations_id')
                             }
                   }

        url = self.url+"/Ticket"
        response = GlpiApiRequest.request(headers=self.headers, url=url, payload=payload, request_type='post')

        if response.status_code >= 400:
            return None

        self.ticket.id = response.json().get('id')

        # Assign equipment with ticket
        equipment_id = equipment_or_location.get('equipment_id')
        if theme == Config.BTN_THEME_EQIPMENT and equipment_id is not None:
            self._create_assign_equipment(equipment_id)

        return self.ticket.id

    def _get_equipment_or_location(self, search_name, theme):
        equipment_or_location = {'equipment_id': None, 'locations_id': 0}
        if theme == Config.BTN_THEME_ROOM:
            location_id = self._get_location_id(search_name)
            if location_id is not None:
                return {'equipment_id': None, 'locations_id': location_id}
        if theme == Config.BTN_THEME_EQIPMENT:
            equipment = self._get_equipment_id(search_name)
            if equipment is not None:
                return {'equipment_id': equipment.get('equipment_id'), 'locations_id': equipment.get('locations_id')}
        return equipment_or_location

    def _get_location_id(self, loc_name):
        url = f'{self.url}/Location/?searchText[name]={loc_name}'
        response = GlpiApiRequest.request(headers=self.headers, url=url, payload=None, request_type='get')
        if response.status_code >= 400 or len(response.json()) == 0:
            return None
        else:
            return response.json()[0]['id']

    def _get_equipment_id(self, eq_name):
        url = f'{self.url}/Peripheral/?searchText[name]={eq_name}'
        response = GlpiApiRequest.request(headers=self.headers, url=url, payload=None, request_type='get')
        if response.status_code >= 400 or len(response.json()) == 0:
            return None
        else:
            return {'equipment_id': response.json()[0].get('id'),
                    'locations_id': response.json()[0].get('locations_id')}

    def _create_assign_equipment(self, equipment_id):
        url = f'{self.url}/Ticket/{self.ticket.id}/Item_Ticket/'
        payload = {"input": {"tickets_id": self.ticket.id,
                             "items_id": equipment_id,
                             "itemtype": "Peripheral"}
                   }
        GlpiApiRequest.request(headers=self.headers, url=url, payload=payload, request_type='post')

    def create_project(self):
        if self.project.id is None:
            if self.project.content == '':
                self.project.content = self.project.name

            payload = {"input": {"name": self.project.name,
                                 "content": self.project.content,
                                 "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 "users_id": self.user.id,
                                 "priority": 3,
                                 "projectstates_id": 0
                                 }
                       }
            url = self.url+"/Project"
            response = GlpiApiRequest.request(headers=self.headers, url=url, payload=payload, request_type='post')

            if response.status_code >= 400:
                return None

            self.project.id = response.json().get('id')

            if response.status_code == 201:
                self.project.id = json.loads(response.text).get('id')

        if self.project.id:
            payload = {"input": {"projects_id": self.project.id,
                                 "itemtype": "User",
                                 "items_id": Config.PROJECT_MANAGER_ID
                                 }
                       }

            url = f"{self.url}/Project/{self.project.id}/ProjectTeam"
            GlpiApiRequest.request(headers=self.headers, url=url, payload=payload, request_type='post')

        return self.project.id

    def _get_id_and_type(self):
        if self.ticket is not None:
            return self.ticket.id, "Ticket"
        if self.project is not None:
            return self.project.id, "Project"

    def upload_doc(self, file_path, filename, doc_name):
        document_id = None
        headers = {'Session-Token': self.session}
        files = {'uploadManifest': (None, '{"input": {"name": "' + doc_name +
                                    ' (tb)", "_filename": ["' + filename + '"]}}', 'application/json'),
                 'filename[0]': (filename, open(file_path + '/' + filename, "rb")), }

        url = self.url+"/Document"
        response = requests.post(url, headers=headers, files=files)
        if response:
            logger.info(f'{url} status_code={response.status_code}')
            if response.status_code >= 400:
                logger.warning(f'{url} error = {response.text}')

        if response.status_code in range(200, 300):
            document_id = response.json().get('id')

        return document_id

    def link_loaded_doc_to_item(self, document_id):
        item_id = self._get_id_and_type()[0]
        item_type = self._get_id_and_type()[1]

        payload = {"input": {"documents_id": document_id,
                             "items_id": item_id,
                             "itemtype": item_type,
                             "users_id": self.user.id,
                             "is_recursive": 1,
                             }
                   }
        url = f"{self.url}/Document/{document_id}/Document_Item"
        response = GlpiApiRequest.request(url=url, headers=self.headers, payload=payload, request_type='post')
        return response.status_code


class GlpiApiRequest:
    @classmethod
    def request(cls, headers: dict, url: str, payload: dict | None, request_type: str):

        response = None

        if request_type == 'post':
            response = requests.post(url, headers=headers, json=payload)
        if request_type == 'put':
            response = requests.put(url, headers=headers, json=payload)
        if request_type == 'get':
            response = requests.get(url, headers=headers, json=payload)

        # if response is not None:
        logger.info(f'{url} status_code={response.status_code}')
        if response.status_code >= 400:
            logger.warning(f'api_request {url} error = {response.text}')

        return response


def api_request(headers: dict, url: str, payload: dict, request_type: str):
    data = json.dumps(payload).encode('utf-8')

    response = None

    if request_type == 'post':
        response = requests.post(url, headers=headers, data=data)
    if request_type == 'put':
        response = requests.put(url, headers=headers, data=data)

    # if response:
    logger.info(f'{url} status_code={response.status_code}')
    if response.status_code >= 400:
        logger.warning(f'api_request {url} error = {response.text}')

    return response


def solve_ticket(chat_id, ticket_id):
    headers = glpi_dict[chat_id].headers
    payload = {"input": {"items_id": ticket_id,
                         "content": Config.MSG_SOLUTION,
                         "users_id": glpi_dict[chat_id].user.id,
                         "solutiontypes_id": 0,
                         "itemtype": "Ticket",
                         "status": 5,
                         }
               }

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
    payload = {"input": {"itemtype": "Ticket",
                         "items_id": ticket_id,
                         "users_id": glpi_dict[chat_id].user.id,
                         "content": Config.MSG_APPROVAL,
                         }
               }
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    request_list.append((url, payload, 'post'))

    # PUT to last solution
    payload = {"input": {"items_id": ticket_id,
                         "users_id_approval": glpi_dict[chat_id].user.id,
                         "solutiontypes_id": 1,
                         "itemtype": "Ticket",
                         "status": 3
                         }
               }
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

    # if response:
    logger.info(f'{url} status_code={response.status_code}')
    if response.status_code >= 400:
        logger.warning(f'api_request {url} error = {response.text}')

    if response.status_code == 200:
        solution_id = json.loads(response.content)[-1]['id']
    else:
        return

    request_list = []

    # POST comment approval
    payload = {"input": {"itemtype": "Ticket",
                         "items_id": ticket_id,
                         "users_id": glpi_dict[chat_id].user.id,
                         "content": msg_reason,
                         }
               }
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    request_list.append((url, payload, 'post'))

    # PUT to last solution
    payload = {"input": {"items_id": ticket_id,
                         "users_id": 0,
                         "users_id_approval": glpi_dict[chat_id].user.id,
                         "solutiontypes_id": 0,
                         "itemtype": "Ticket",
                         "status": 4,
                         }
               }
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

    # if response:
    logger.info(f'{url} status_code={response.status_code}')
    if response.status_code >= 400:
        logger.warning(f'api_request {url} error = {response.text}')

    if response.status_code == 200:
        return json.loads(response.content)['status']
    else:
        return 0


def leave_ticket_comment(chat_id, ticket_id, comment):
    headers = glpi_dict[chat_id].headers

    # POST comment
    payload = {"input": {"itemtype": "Ticket",
                         "items_id": ticket_id,
                         "users_id": glpi_dict[chat_id].user.id,
                         "content": comment,
                         }
               }
    url = f'{Config.URL_GLPI}/Ticket/{ticket_id}/ITILFollowup'
    return api_request(headers, url, payload, 'post')


def get_user_projects(chat_id):
    headers = glpi_dict[chat_id].headers
    user_id = user_dict[chat_id].id
    url = f'{Config.URL_GLPI}/User/{user_id}/Project'
    response = requests.get(url, headers=headers)

    # if response:
    logger.info(f'{url} status_code={response.status_code}')
    if response.status_code >= 400:
        logger.warning(f'{url} error = {response.text}')
        return []
    projects = response.content
    return json.loads(projects)
    # return []


if __name__ == '__main__':
    print('glpiapi module')
