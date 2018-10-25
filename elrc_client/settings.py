import logging

REPO_URL = 'http://localhost:8000'
LOGIN_URL = '%s/login/' % REPO_URL
LOGOUT_URL = '%s/logout/' % REPO_URL
API_ENDPOINT = '%s/repository/api/editor/lr/' % REPO_URL
API_OPERATIONS = '%s/repository/api/operations/' % REPO_URL
XML_UPLOAD_URL = '%s/repository/api/create/' % REPO_URL
XML_SCHEMA = 'https://elrc-share.eu/ELRC-SHARE_SCHEMA/v2.0/ELRC-SHARE-Resource.xsd'

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] ELRC::%(levelname)-5.5s  %(message)s",
    handlers=[
        logging.StreamHandler()
    ])
