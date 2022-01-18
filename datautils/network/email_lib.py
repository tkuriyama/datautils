"""A lightweight SMTP email sender.
"""

from email.mime.text import MIMEText  # type: ignore
import logging  # type: ignore
from smtplib import SMTP_SSL as SMTP  # type: ignore
import sys  # type: ignore
from typing import (List, TypedDict)  # type: ignore

from datautils.core import log_setup  # type: ignore

##########################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)

##########################################################################


class AuthDict(TypedDict):
    user: str
    pwd: str


Html = str

##########################################################################


def send(subject: str,
         fromAddr: str,
         toAddrs: List[str],
         body: Html,
         server: str,
         auth: AuthDict
         ) -> None:
    """Send SMTP email with Html body."""

    fromAddr = fromAddr.strip()
    toAddrs = [addr.strip() for addr in toAddrs]

    # hard-coded assertions on addresses, e.g. domain checks
    assert all('@' in addr for addr in [fromAddr] + toAddrs)

    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = fromAddr
    msg['To'] = ','.join(toAddrs)

    conn = SMTP(server)
    conn.set_debuglevel(False)
    conn.login(auth['user'], auth['pwd'])

    try:
        conn.sendmail(fromAddr, ','.join(toAddrs), msg.as_string())
        logger.info('Email sent')
    except Exception as e:
        logger.error('Email send failed: {}'.format(e))
        sys.exit('Send failed: {}'.format(e))
    finally:
        conn.quit()
        logger.debug('SMTP connection closed')
