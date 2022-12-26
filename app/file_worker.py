import shutil
from app.settings import settings

def write_file(file):
    with open(f'{settings.FILE_CONTAINER_NAME}/{file.filename}', 'wb') as f:
        shutil.copyfileobj(file.file, f)