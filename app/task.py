from time import sleep
from datetime import datetime
from datetime import timedelta

from . import db
from .models import Code
from .models import Token


def loop(app):
    while True:
        with app.app_context():
            now = datetime.now()

            ttl = timedelta(minutes=10)
            for code in Code.query.limit(250).all():
                if not now <= code.date + ttl:
                    db.session.delete(code)

            db.session.commit()

            ttl = timedelta(days=7)
            for token in Token.query.limit(250).all():
                if not now <= token.date + ttl:
                    db.session.delete(token)

            db.session.commit()

        sleep(2700)  # 45 * 60
