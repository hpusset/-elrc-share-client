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

import sys

import os

sys.path.append('C:\\Users\\Unicorn\\PycharmProjects\\elrc_client')

from unittest import TestCase, main
from elrc_client.settings import DOWNLOAD_DIR
from elrc_client.client import ELRCShareClient


class TestAuth(TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        cls.client = ELRCShareClient()

    @classmethod
    def tearDownClass(cls):
        cls.client.logout()
        cls.client = None

    def setUp(self):
        print("Running Test:", self._testMethodName)

    # Test that an existing user "test":"test" can login to the site
    def test_existing_user_can_log_in(self):
        self.client.login("test", "test")

        self.assertTrue(self.client.logged_in)
        self.client.logout()

    def test_non_existing_user_cannot_log_in(self):
        self.client.login("no_user", "no_pwd")
        self.assertFalse(self.client.logged_in)


class TestOperations(TestCase):
    client = None
    users = {
        'admin': {'usr': 'admin', 'pwd': 'admin'},
        'ecuser': {'usr': 'ecuser', 'pwd': 'ecuser'},
        'reviewer': {'usr': 'reviewer', 'pwd': 'reviewer'},
        'contributor': {'usr': 'contributor', 'pwd': 'contributor'}
    }

    @classmethod
    def setUpClass(cls):
        cls.client = ELRCShareClient()

    @classmethod
    def tearDownClass(cls):
        cls.client.logout()
        cls.client = None

    def setUp(self):
        print("Running Test:", self._testMethodName)

    def test_admin_can_download_datasets(self):
        self.client.login(self.users['admin']['usr'], self.users['admin']['pwd'])
        self.client.download_data(9)
        self.assertTrue(os.path.exists(os.path.join(DOWNLOAD_DIR, 'archive-9.zip')))
        os.remove(os.path.join(DOWNLOAD_DIR, 'archive-9.zip'))
        self.client.logout()

    def test_admin_can_create_resource(self):
        self.client.login(self.users['admin']['usr'], self.users['admin']['pwd'])
        response = self.client.create_resources('tests/fixtures/test.xml')
        self.assertTrue(response, 201)




if __name__ == '__main__':
    main()
