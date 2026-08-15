# Desktop_Companion

install dependancies
    fastapi
    uvicorn
    psutil
    pywin32
    websockets
    requests

cd D:\Projects\DeskMate ( cd .. )
python sensor/watcher.py
uvicorn server.main:app --reload

cd avatar
npm init -y
npm electron --save-dev
npm start

