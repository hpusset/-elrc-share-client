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

import logging

import os

# import local_settings

TEST_MODE = False

if TEST_MODE:
    REPO_URL = ''  # dev url
else:
    REPO_URL = 'https://elrc-share.eu'
LOGIN_URL = '%s/login/' % REPO_URL
LOGOUT_URL = '%s/logout/' % REPO_URL
API_ENDPOINT = '%s/repository/api/editor/lr/' % REPO_URL
API_OPERATIONS = '%s/repository/api/operations/' % REPO_URL
XML_UPLOAD_URL = '%s/repository/api/create/' % REPO_URL
XML_SCHEMA = 'https://elrc-share.eu/ELRC-SHARE_SCHEMA/v2.0/ELRC-SHARE-Resource.xsd'

# Set default directory for downloads
if os.name == 'posix':
    DOWNLOAD_DIR = '/home/{}/ELRC-Downloads'.format(os.getlogin())
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
elif os.name == 'nt':
    DOWNLOAD_DIR = 'C:\\Users\\{}\\Downloads\\ELRC-Downloads'.format(os.getlogin())

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] ELRC-SHARE::%(levelname)-5.5s  %(message)s",
    handlers=[
        logging.StreamHandler()
    ])
