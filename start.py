
from waitress import serve
from paste.translogger import TransLogger

from app import create_app


if __name__ == "__main__":
    serve(TransLogger(create_app()), port=16484)
