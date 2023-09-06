import datetime
import requests
import json
from app.config import Config
from app.utils.glpidb import get_equipment_id, get_location_id

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


class GLPI:
    def __init__(self, url=None, user=None, ticket=None):
        self.url = url
        self.user = user
        self.ticket = ticket
        # User session initialization
        headers = {
            "Content-Type": "application/json",
            "Authorization": "user_token " + self.user.token
        }
        response = requests.get(self.url+"/initSession", headers=headers)
        if response.status_code == 401 or response.status_code == 400:
            self.session = None
        else:
            self.session = json.loads(response.text).get('session_token')

    def __del__(self):
        """
        :return: kill user session when destroy object
        """
        headers = {
            'Content-Type': 'application/json',
            'Session-Token': self.session,
        }
        requests.get(self.url+"/killSession", headers=headers)

    def create_ticket(self):
        """
        :return: ticket_id
        """
        if self.ticket.id is None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "user_token " + self.user.token,
                "Session-Token": self.session
            }
            if self.ticket.content == '':
                self.ticket.content = self.ticket.name

            itilcategories_id = self.ticket.category_id
            urgency_id = self.ticket.urgency_id

            time_to_resolve = str(datetime.datetime.today().date() + datetime.timedelta(5)) + ' 12:00:00'

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

            msg = json.dumps(msg_dict).encode('utf-8')
            response = requests.post(self.url+"/Ticket", headers=headers, data=msg)
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
                    msg = json.dumps(msg_dict).encode('utf-8')
                    response = requests.post(url, headers=headers, data=msg)
                    logger.info(f'{url} status_code={response.status_code}')

        return self.ticket.id

    def upload_doc(self, file_path, filename):
        """
        :param file_path: path to downloaded files
        :param filename: from 'ticket.attachment'
        :return: noting
        """
        headers = {'Session-Token': self.session}
        files = {'uploadManifest': (None, '{"input": {"name": "Документ заявки '+str(self.ticket.id) +
                                    ' (tb)", "_filename": ["' + filename + '"]}}', 'application/json'),
                 'filename[0]': (filename, open(file_path + '/' + filename, "rb")), }

        response = requests.post(self.url+"/Document", headers=headers, files=files)

        if response.status_code == 201:
            doc_id = response.json().get('id')
        else:
            doc_id = None

        return doc_id


if __name__ == '__main__':
    print('glpiapi module')
