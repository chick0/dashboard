from sqlalchemy import func

from . import db


# 유저:
#   유저 아이디
#   유저 이메일
#   유저 비밀번호
#   유저 닉네임
#   유저 가입날짜
class User(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    email = db.Column(
        db.String(128),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(128),
        nullable=False
    )

    nickname = db.Column(
        db.String(32),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    def __repr__(self):
        return f"<User idx={self.idx}, email={self.email!r}>"


# 로그인 기록:
#   기록 고유 번호
#   로그인 대상 이메일
#   로그인 성공 여부
#   로그인 시도 IP 주소
#   로그인 시도 클라이언트의 에이전트 값
#   로그인 시도 날짜
class History(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    email = db.Column(
        db.String(128),
        nullable=False
    )

    is_failed = db.Column(
        db.Boolean,
        nullable=False
    )

    ip = db.Column(
        db.String(64),
        nullable=False
    )

    user_agent = db.Column(
        db.String(200),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    def __repr__(self):
        return f"<History idx={self.idx}, email={self.date!r}>"


# 어플리케이션:
#   아이디
#   이름
#   소유자 아이디
#   등록날짜
#   홈페이지
#   콜백 링크
class Application(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    name = db.Column(
        db.String(20),
        nullable=False
    )

    owner_idx = db.Column(
        db.Integer,
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    homepage = db.Column(
        db.String(32),
        nullable=False
    )

    callback = db.Column(
        db.String(500),
        nullable=False
    )

    delete = db.Column(
        db.Boolean,
        nullable=False
    )

    def __repr__(self):
        return f"<Application idx={self.idx}, owner_idx={self.owner_idx}>"


# 어플리케이션 시크릿:
#   어플리케이션 아아디
#   시크릿 키
#   시크릿 생성 날짜
class ApplicationSecret(db.Model):
    target_idx = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )

    key = db.Column(
        db.String(64),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    def __repr__(self):
        return f"<ApplicationSecret idx={self.idx}, target_idx={self.target_idx}>"


# 토큰 생성 코드:
#   앱 아이디
#   타겟 유저 아이디
#   스코프 (=권한)
#   코드
#   코드 생성 날짜
class Code(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    application_idx = db.Column(
        db.Integer,
        nullable=False
    )

    target_idx = db.Column(
        db.Integer,
        nullable=False
    )

    scope = db.Column(
        db.String(64),
        nullable=False
    )

    code = db.Column(
        db.String(32),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    def __repr__(self):
        return f"<Code idx={self.idx}, application_idx={self.application_idx}, target_idx={self.target_idx}>"


# 접속 토큰:
#   앱 아이디
#   타겟 유저 아이디
#   스코프 (=권한)
#   토큰
#   토큰 생성 날짜
class Token(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    application_idx = db.Column(
        db.Integer,
        nullable=False
    )

    target_idx = db.Column(
        db.Integer,
        nullable=False
    )

    scope = db.Column(
        db.String(64),
        nullable=False
    )

    token = db.Column(
        db.String(128),
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    def __repr__(self):
        return f"<Token idx={self.idx}, idx={self.application_idx}, target_idx={self.target_idx}>"


# 2단계 인증:
#   유저 아이디
#   인증 토큰
class TwoFactor(db.Model):
    user_idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    secret = db.Column(
        db.String(40),
        nullable=False
    )

    def __repr__(self):
        return f"<TwoFactor user_idx={self.user_idx}>"
