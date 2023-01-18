# OAuth-dashboard

OAuth 대시보드 프로젝트는 OAuth 기능을 제공하는 웹 사이트 입니다.

## 서버 시작하기

1. 의존성 설치하기

   ```bash
   pip install -r requirements.txt
   ```

2. 설정하기 (설정하기 섹션 참고)

3. 서버 실행하기

   ```bash
   gunicorn -c gunicorn.py
   ```

## 설정하기

1. **필수** 데이터베이스 접속 링크 설정하기

    ```bash
    export dashboard_sql='mysql://<id>:<password>@<host>:<port>/<db name>'
    ```

2. **필수** SMTP 계정 설정하기

    ```bash
    export dashboard_smtp_host='smtp.example.com'
    export dashboard_smtp_post='587'
    export dashboard_smtp_user='user@example.com'
    export dashboard_smtp_password='password'
    ```

3. 비밀번호 솔트 설정하기

    ```bash
    export dashboard_salt_password=''
    ```

    - 주의사항 : 이 설정 값이 변경되면 기존 계정에 로그인 할 수 없습니다.

4. gunicorn 설정

   - `gunicorn.py` 파일이 설정 파일 입니다. [자세한 정보](https://docs.gunicorn.org/en/stable/settings.html)
