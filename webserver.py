from excel_handler import get_users_from_excel
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager #Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
from typing import Optional
from config import *
from hasher import Hasher
import nginx
import pathlib
import uvicorn
import os

app = FastAPI()

templates_path = pathlib.Path(__file__).parent.resolve() / 'templates'
templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=templates_path / 'static'), name="static")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hidden_imports=[
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    # 'app',
]

def get_nginx_config():
    BASE_DIR = pathlib.Path(__file__).parent
    print(BASE_DIR)

    payload = nginx.Conf()
    s = nginx.Server()
    s.add(
        nginx.Key('server_name', '<DOMAIN_NAME>'),
        nginx.Location('/',
            nginx.Key('proxy_pass', 'http://localhost:8000')
        )
    )

    payload.add(s)
    nginx.dumpf(payload, os.path.join(BASE_DIR, '/etc/nginx/sites-enabled/ticket'))
    # nginx.dumpf(payload, '/etc/nginx/sites-enabled/ticket')
    return True

users_entrance = {}
# To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())
# Convert the string to bytes using the 'encode()' method
SECRET_BYTES = SECRET.encode()

# Now use SECRET_BYTES in the LoginManager
manager = LoginManager(SECRET_BYTES, token_url="/auth/login", use_cookie=True)
manager.cookie_name = "auth"

DB = {"admin":{"password":Hasher.get_password_hash(ADMIN_PASSWORD)}} # unhashed

@manager.user_loader
def load_user(username:str):
    user = DB.get(username)
    return user

@app.get("/auth/login", response_class=HTMLResponse)
def loginwithCreds(request:Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    user = load_user(username)
    
    if not user:
        raise InvalidCredentialsException

    elif not Hasher.verify_password(password, user['password']):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
    data={"sub":username})
    resp = RedirectResponse(url="/reception", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, access_token)
    return resp
        

@app.get("/reception", response_class=HTMLResponse)
async def reception_page(request: Request, _=Depends(manager)):
    return templates.TemplateResponse("reception.html", {"request": request,
                                                         "base_url": DOMAIN_NAME,
                                                         "page_title": PAGE_TITLE})

@app.get("/api/reception/{ticket_id}")
async def verify_ticket(ticket_id: int):
    for user in get_users_from_excel(OUTPUT_FILE_PATH):
        if user['ticket_id'] == ticket_id:
            if ticket_id in users_entrance:
                users_entrance[ticket_id] += 1
            else:
                users_entrance[ticket_id] = 1

            return {
                'name': user['name'],
                'status': user['status'],
                'entrance_count': users_entrance[ticket_id]
            }

@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def ticket(request: Request, ticket_id: int):
    return templates.TemplateResponse("ticket.html", {"request": request,
                                                      "ticket_id": ticket_id,
                                                      "base_url": DOMAIN_NAME,
                                                      "page_title": PAGE_TITLE,
                                                      "event_name": EVENT_NAME})


@app.get("/api/ticket/all")
async def read_all_items():
    return {"users": get_users_from_excel(OUTPUT_FILE_PATH), "users_entrance": users_entrance}

@app.get("/api/ticket/{ticket_id}")
async def read_items(ticket_id: int):
    for user in get_users_from_excel(OUTPUT_FILE_PATH):
        if user['ticket_id'] == ticket_id:
            return user
    raise HTTPException(status_code=404, detail="User Not Found")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "page_title": PAGE_TITLE})


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # uvicorn.run(app)

# if __name__ == '__main__':
    # run_server()
    