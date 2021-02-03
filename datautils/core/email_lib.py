"""A lightweight SMTP email sender.
"""

from email.mime.text import MIMEText # type: ignore
from smtplib import SMTP_SSL as SMTP # type: ignore
import sys # type: ignore
from typing import (List, TypedDict) # type: ignore

################################################################################

class AuthDict(TypedDict):
    user: str
    pwd: str

Html = str

################################################################################

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
    except Exception as e:
        sys.exit('Send failed: {}'.format(e))
    finally:
        conn.quit()
