```bash
pip intall -r requirements.txt
```

```bash
uvicorn --port 8000 --loop uvloop --interface wsgi --factory app:create_app
```
