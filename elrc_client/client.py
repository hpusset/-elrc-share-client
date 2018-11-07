# Copyright 2018 ILSP/Athena R.C. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the following
#     disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials
#     provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY ILSP/Athena R.C. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ILSP/Athena R.C. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of ILSP/Athena R.C.

import atexit
import json
import sys
import zipfile

import os
import requests
from elrc_client.settings import LOGIN_URL, API_ENDPOINT, LOGOUT_URL, API_OPERATIONS, DOWNLOAD_DIR
from elrc_client.settings import logging
from elrc_client.utils.data_merger import get_update_with_ids
from elrc_client.utils.xml import parser


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict, ensure_ascii=False))


class ELRCShareClient:
    def __init__(self):
        self.session = None
        self.csrftoken = None
        self.user_log_in = None
        self.logged_in = False
        self.headers = {
            'Content-Type': 'application/json'
        }

        atexit.register(self.logout)

    def login(self, username, password):
        try:
            self.session = requests.session()
            self.user_log_in = self.session.get(LOGIN_URL)
            self.csrftoken = self.session.cookies['csrftoken']
            if self.user_log_in.ok:
                login_data = {
                    'username': username,
                    'password': password,
                    'csrfmiddlewaretoken': self.csrftoken
                }
                # Login to site
                try:
                    login = self.session.post(LOGIN_URL, data=login_data)
                    if 'Your username and password didn\'t match' in login.text:
                        logging.error('Unsuccessful Login...')
                    else:
                        self.logged_in = True
                        logging.info('Login Successful!')
                except requests.exceptions.ConnectionError:
                    logging.error('Could not connect to remote host.')
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def logout(self):
        """
        Logout user and close session when program exits
        """
        if self.logged_in:
            try:
                self.session.get(LOGOUT_URL)
                self.session.close()
                self.logged_in = False
                logging.info("Logout....")
            except requests.exceptions.ConnectionError:
                logging.error('Could not connect to remote host.')
        else:
            pass

    def get_resource(self, rid=None, as_json=False, as_xml=False, pretty=False):
        """
        Given an ELRC-SHARE Language Resource id, return the resource's metadata
        in a python dictionary.

        :param rid: ELRC Resource ID
        :param as_json: Boolean value. If False, the method returns a dictionary, else a json string
        :return: Python dictionary or json containing resource metadata
        """
        if as_xml:
            url = "{}get_xml/{}/".format(API_OPERATIONS, rid)
        else:
            url = "{}{}".format(API_ENDPOINT, rid)

        indent = 4 if pretty else None
        try:
            request = self.session.get(url)
            request.encoding = 'utf-8'
            if request.status_code == 401:
                return '401 Unauthorized Request'
            elif request.status_code == 400:
                return '400 Bad Request'
            elif request.status_code == 404:
                return 'Resource with rid {} was not found'.format(rid)
            if as_json:
                return json.dumps(json.loads(request.content), ensure_ascii=False, indent=indent)
            elif as_xml:
                return request.text
            else:
                return json.loads(request.content)
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def get_my_resources(self, as_json=True, as_xml=False, pretty=False):
        """
        Given an ELRC-SHARE Language Resource id, return the resource's metadata
        in a python dictionary.

        :param id: ELRC Resource ID
        :param as_json: Boolean value. If False, the method returns a dictionary, else a json string
        :return: Python dictionary or json containing resource metadata
        """
        indent = 4 if pretty else None
        try:
            request = self.session.get(API_ENDPOINT + '?limit=0')
            if request.status_code == 401:
                return '401 Unauthorized Request'
            elif request.status_code == 400:
                return '400 Bad Request'
            elif request.status_code == 404:
                return 'Resource with id {} was not found'.format(id)
            if as_json:
                return json.dumps(json.loads(request.content), ensure_ascii=False, indent=indent)
            else:
                return json.loads(request.content)
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def update_resource(self, id, xml_file=None):
        """
        Given an ELRC-SHARE Language Resource id, update the corresponding resource.

        :param id: ELRC Resource ID for the resource to be updated
        :param data: A python dictionary containing the data to be passed for updating the resource
        :return: status code (expected 202)
        """
        url = "{}{}".format(API_ENDPOINT, id)
        # populate
        data = parser.parse(open(os.path.join(os.path.dirname(__file__), xml_file), encoding='utf-8').read())
        remote_resource = self.get_resource(id)
        if type(remote_resource) is not dict:
            logging.error(remote_resource)
        else:
            final = get_update_with_ids(self.get_resource(id), to_dict(data))
            print(final)
            # final = to_dict(data)
            final['resourceInfo']['id'] = id

            try:
                request = self.session.patch(url, headers=self.headers,
                                             data=json.dumps(final, ensure_ascii=False).encode('utf-8'))
                print(request.status_code, request.content)
                return request.status_code, request.content
            except requests.exceptions.ConnectionError:
                logging.error('Could not connect to remote host.')

    def create_resource(self, description, dataset=None):
        resource_name = description.get('resourceInfo').get('identificationInfo').get('resourceName').get('en')
        # print(json.dumps(description, ensure_ascii=False))
        try:
            request = self.session.post(API_ENDPOINT, headers=self.headers,
                                        data=json.dumps(description, ensure_ascii=False).encode('utf-8'))

            if request.status_code == 201:
                print("Metadata created".format(resource_name))
                new_id = json.loads(request.content).get('ID')
                try:
                    self.upload_data(new_id, dataset)
                except Exception as e:
                    pass
                print("Resource '{}' has been created\n".format(resource_name))
                return
            elif request.status_code == 401:
                logging.error('401 Unauthorized Request')
                return
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def upload_data(self, resource_id, data_file):

        if not zipfile.is_zipfile(data_file):
            logging.error('Not a valid zip archive')
            return
        else:
            try:
                del self.headers['Content-Type']
            except KeyError:
                pass
            self.headers.update({'X-CSRFToken': self.session.cookies['csrftoken']})
            url = "{}upload_data/{}/".format(API_OPERATIONS, resource_id)

            files = {'resource': open(data_file, 'rb')}
            data = {
                'csrfmiddlewaretoken': self.session.cookies['csrftoken'],
                'uploadTerms': 'on',
                'api': True}

            print('Attempting dataset upload...')
            response = self.session.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            print(response.text)

    def create_resources(self, file, dataset=None):
        if zipfile.is_zipfile(file):
            zip_file = zipfile.ZipFile(file)
            for f in zip_file.namelist():
                logging.info('Processing file: {}'.format(f))
                data = parser.parse(zip_file.open(f).read())
                self.create_resource(data)
        else:
            logging.info('Processing file: {}'.format(file))
            data = parser.parse(open(os.path.join(os.path.dirname(__file__), file), encoding='utf-8').read())

            self.create_resource(data, dataset=dataset)

    def download_data(self, resource_id, destination='', progress=True):
        if self.logged_in:
            if not destination:
                destination = DOWNLOAD_DIR
            try:
                url = "{}get_data/{}/".format(API_OPERATIONS, resource_id)
                head = self.session.head(url)
                try:
                    if head.headers.get('Content-Type') != 'application/zip':
                        if head.status_code == 200:
                            # returns a page with the message "No Download Available"
                            logging.error('Dataset for resource {} was not found\n'.format(resource_id))
                            return None
                        if head.status_code == 401:
                            logging.error('401 Unauthorized Request')
                            return None
                        elif head.status_code == 400:
                            logging.error('400 Bad Request')
                            return None
                        elif head.status_code == 404:
                            logging.error('Dataset for resource {} was not found'.format(resource_id))
                            return None
                        elif head.status_code == 500:
                            logging.error('Resource with id {} was not found'.format(resource_id))
                            return None
                        elif head.status_code == 403:
                            logging.error('Forbidden operation on resource with id {}.'.format(resource_id))
                            return None
                        elif 'No Download Available' in head.text:
                            logging.error('No download available for resource with id {}.'.format(resource_id))
                            return None
                    else:
                        logging.info('Downloading resource with id {}'.format(resource_id))
                        try:
                            destination_file = self._provide_download(url, resource_id, destination, progress=progress)
                            logging.info("Download complete at {}\n".format(destination_file))
                        except RuntimeError:
                            logging.error("Could not write file. Unknown runtime error occurred.")
                except RuntimeError:
                    pass
                return True
            except requests.exceptions.ConnectionError:
                logging.error('Could not connect to remote host.')
        else:
            logging.error("Please login to ELRC-SHARE using your credentials")

    def _provide_download(self, url, resource_id, destination, progress):
        # Check if destination directory is provided an whether it exists. If not create it
        if destination:
            os.makedirs(destination, exist_ok=True)
        destination_file = os.path.join(destination, "archive-{}.zip".format(resource_id))
        with open(destination_file, 'wb') as f:
            response = self.session.get(url, stream=True)
            total = response.headers.get('content-length')

            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / total)
                    if progress:
                        sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50 - done)))
                        sys.stdout.flush()
        if progress:
            sys.stdout.write('\n')
        return destination_file
