"""Lightweight wrapper for the requests library.
"""

import json # type: ignore
import logging # type: ignore
import requests # type: ignore
from typing import Dict, List, Optional, TypedDict # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.core.utils import Error, OK, Status # type: ignore

################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################

class AuthDict(TypedDict):
    user: str
    pwd: str

MaybeAuth = Optional[AuthDict]


################################################################################
# Get

def get(url: str, auth: MaybeAuth = None) -> requests.Response:
    """Simple Get."""
    if auth:
        r = requests.get(url, auth=(auth['user'], auth['pwd']))
    else:
        r = requests.get(url)
    if r.status_code != 200:
        logger.warning('Request to {} returned code {}'.format(url,
                                                               r.status_code))
    return r

def get_save_text(url: str, fname: str, auth: MaybeAuth = None) -> Status:
    """Get and attempt to save text response to file."""
    status: Status

    r = get(url, auth)
    if r.text:
        try:
            with open(fname, 'w') as f:
                f.write(r.text)
            status = OK()
        except Exception as e:
            status = Error('Writing to file failed: {}'.format(str(e)))
            logger.error('Write to {} failed: {}'.format(fname, str(e)))
    else:
        msg = 'No text data from {}; code {}'.format(url, r.status_code)
        status = Error(msg)
        logger.info(msg)

    return status

def get_save_json(url: str, fname: str, auth: MaybeAuth = None) -> Status:
    """Get and attempt to save JSON response to file."""
    status: Status

    r = get(url, auth)
    if r.json:
        try:
            with open(fname, 'w') as f:
                f.write(json.dumps(r.json))
            status = OK()
        except Exception as e:
            status = Error('Writing to file failed: {}'.format(str(e)))
            logger.error('Write to {} failed: {}'.format(fname, str(e)))
    else:
        msg = 'No text data from {}; code {}'.format(url, r.status_code)
        status = Error(msg)
        logger.info(msg)

    return status


################################################################################
# Helpers

def url_join(paths: List[str], params: Optional[Dict[str, str]] = None) -> str:
    """Construct URL with standard REST syntax."""
    url = ''

    # ensure joins with '/' but ignore final '/'
    for path in paths:
        url += path if path[-1] == '/' else '{}/'.format(path)
    url_ = url[:-1]

    if params:
        url_ += '?' + '&'.join('{}={}'.format(k, v) for k, v in params.items())
    return url_
