from random import choices
from smtplib import SMTP
from email.mime.text import MIMEText

from .config import SMTP_HOST
from .config import SMTP_PORT
from .config import SMTP_USER
from .config import SMTP_PASSWORD


def send(target_address: str) -> str:
    for x in [SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]:
        if x == "#":
            raise Exception("SMTP 설정을 발견하지 못함")

    token = "".join(choices(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], k=6))
    html = "<br>\n".join([
        "<h1>이메일 인증 코드</h1>",
        f"<b>{token}</b>",
        "",
        "* 이 인증 코드는 10분뒤에 만료됩니다. *",
    ])

    with SMTP(SMTP_HOST, int(SMTP_PORT)) as client:
        client.login(
            user=SMTP_USER,
            password=SMTP_PASSWORD
        )

        msg = MIMEText(html, "html", "utf-8")
        msg['From'] = SMTP_USER
        msg['Subject'] = "이메일 인증 코드"

        client.sendmail(
            from_addr=SMTP_USER,
            to_addrs=target_address,
            msg=msg.as_string()
        )

    return token
