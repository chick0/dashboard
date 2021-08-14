from multiprocessing import cpu_count

bind = "127.0.0.1:16484"

workers = cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
