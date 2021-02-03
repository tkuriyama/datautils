import sys

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

def send(subject, fromAddr, toAddrs, body, server, auth):
    """Send email.
    Args
        sbject: string of subject
        fromAddr: string of sender addr
        toAddrs: list of string of recipieent addrs
        body: string of message
        server: string of SMTP server
        auth: dict of auth strings with keys 'user', 'pass'
    """
    fromAddr = fromAddr.strip()
    toAddrs = [addr.strip() for addr in toAddrs]

    # hard-coded assertions on addresses, e.g. domain checks
    assert all('@' in addr for addr in [fromAddr] + toAddrs)

    html_body = '<html><body>'
    html_body += '<pre style="font-family: "courier new; font-size: 1rem;">'
    html_body += body + '</pre></body></html>'
    
    msg = MIMEText(html_body, 'html')
    msg['Subject'] = subject
    msg['From'] = fromAddr
    msg['To'] = ','.join(toAddrs)

    conn = SMTP(server)
    conn.set_debuglevel(False)
    conn.login(auth['user'], auth['pass'])
    try:
        conn.sendmail(fromAddr, ','.join(toAddrs), msg.as_string())
    except Exception as e:
        sys.exit('Send failed: {}'.format(e))
    finally:
        conn.quit()
        print('Sent message!')


