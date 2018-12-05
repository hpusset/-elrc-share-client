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
from elrc_client.utils.util import is_xml
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
                    if 'Your username and password didn\'t match' in login.text or login.status_code != 200:
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
        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

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
                return 'Resource with id {} was not found'.format(rid)
            if as_json:
                return json.dumps(json.loads(request.content), ensure_ascii=False, indent=indent)
            elif as_xml:
                return request.text
            else:
                return json.loads(request.content)
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def get_resources(self, as_json=True, as_xml=False, pretty=False, my=False):
        """
        Return the metadata of all resources that the current user owns
        in a python dictionary, xml, or json. If the user is admin or belongs to another privileged group, the method
        return all resources in the repository.

        :param as_json: Boolean value. If True, the method returns a json representation of the resource metadata
        :param as_xml: Boolean value. If True, the method returns an xml representation of the resource metadata
        :param pretty: Boolean value. If True, the method returns the prettified json representation
        :return: Python dictionary or json containing resource metadata
        """
        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        indent = 4 if pretty else None
        if my:
            url = API_ENDPOINT + '/my?limit=0'
        else:
            url = API_ENDPOINT + '?limit=0'
        try:
            request = self.session.get(url)
            if request.status_code == 401:
                return '401 Unauthorized Request'
            elif request.status_code == 400:
                return '400 Bad Request'
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

        # reset headers
        self.headers = {
            'Content-Type': 'application/json'
        }

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        url = "{}{}".format(API_ENDPOINT, id)
        # populate
        data = parser.parse(open(os.path.join(os.path.dirname(__file__), xml_file), encoding='utf-8').read())
        remote_resource = self.get_resource(id)
        if type(remote_resource) is not dict:
            logging.error(remote_resource)
        else:
            final = get_update_with_ids(self.get_resource(id), to_dict(data))
            # final = to_dict(data)
            final['resourceInfo']['id'] = id

            try:
                request = self.session.patch(url, headers=self.headers,
                                             data=json.dumps(final, ensure_ascii=False).encode('utf-8'))
                if request.status_code == 500:
                    request.status_code = 201
                    print(request.status_code, ": Resource Updated")
                else:
                    print(request.text)
                return request.status_code, request.content
            except requests.exceptions.ConnectionError:
                logging.error('Could not connect to remote host.')

    def create_resource(self, description, dataset=None):

        # reset headers
        self.headers = {
            'Content-Type': 'application/json'
        }

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        resource_name = description.get('resourceInfo').get('identificationInfo').get('resourceName').get('en')
        # print(json.dumps(description, ensure_ascii=False))
        # Tool/Service not supported
        if description.get('resourceInfo').get('resourceComponentType').get('toolServiceInfo'):
            logging.error("Tool/Services are not yet supported")
            return
        try:
            request = self.session.post(API_ENDPOINT, headers=self.headers,
                                        data=json.dumps(description, ensure_ascii=False).encode('utf-8'))

            if request.status_code == 201:
                print("Metadata created")
                new_id = json.loads(request.content).get('ID')
                try:
                    self.upload_data(new_id, data_file=dataset)
                except Exception as e:
                    pass
                print("Resource '{}' has been created\n".format(resource_name))
                return request.status_code
            elif request.status_code == 401:
                logging.error('401 Unauthorized Request')
                return request.status_code
            else:
                logging.error('{} Could not create resource'.format(request.status_code))
                for k, v in json.loads(request.text).items():
                    print("\n".join(v))
                return request.status_code, request.content
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')
            return 'Connection Error'

    def create_resources(self, file, dataset=None, input=None):

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        if os.path.isdir(file):
            for f in os.listdir(file):
                data = None
                if is_xml(f):
                    logging.info('Processing file: {}'.format(f))
                    with open(os.path.join(file, f), encoding='utf-8') as inp:
                        data = parser.parse(inp.read())
                    attached_dataset = os.path.join(file, f.replace('.xml', '.zip'))
                    if zipfile.is_zipfile(attached_dataset):
                        logging.info('Dataset {} found'.format(attached_dataset))
                        self.create_resource(data, dataset=attached_dataset)
                    else:
                        self.create_resource(data)
        else:
            logging.info('Processing file: {}'.format(file))
            with open(os.path.join(os.path.dirname(__file__), file), encoding='utf-8') as f:
                data = parser.parse(f.read())
            return self.create_resource(data, dataset=dataset)

    def upload_data(self, resource_id, data_file):

        # reset headers
        self.headers = {
            'Content-Type': 'application/json'
        }

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        # determine dataset by resource filename
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
            data = {
                'csrfmiddlewaretoken': self.session.cookies['csrftoken'],
                'uploadTerms': 'on',
                'api': True}

            print('Uploading dataset {} ({:,.2f}Mb)'.format(data_file, os.path.getsize(data_file) / (1024 * 1024.0)))
            # response = self.session.post(
            #     url,
            #     headers=self.headers,
            #     files=files,
            #     data=data
            # )

            with open(data_file, 'rb') as f:
                response = self.session.post(url, files={'resource': f}, data=data)
                # self.session.post(url, dat)
                print(response.text)

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
