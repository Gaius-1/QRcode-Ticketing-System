from config import *
from excel_handler import get_users_from_excel
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import nginx
import pathlib
import uvicorn

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

users_entrance = {}

def get_nginx_config():
    BASE_DIR = pathlib.Path(__file__).parent.resolve()
    os.path.join(BASE_DIR, 'app/laundryman_frontend/build/static')

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

def has_permission(password: str):
    if password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password required")
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    else:
        return True


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "page_title": PAGE_TITLE})


@app.get("/ticket/{ticket_id}", response_class=HTMLResponse)
async def ticket(request: Request, ticket_id: int):
    return templates.TemplateResponse("ticket.html", {"request": request,
                                                      "ticket_id": ticket_id,
                                                      "base_url": DOMAIN_NAME,
                                                      "page_title": PAGE_TITLE,
                                                      "event_name": EVENT_NAME})


@app.get("/api/ticket/all")
# async def read_all_items(password: Optional[str] = None):
async def read_all_items():
    # if has_permission(password):
    #     return users_entrance, users
    return {"users": get_users_from_excel(OUTPUT_FILE_PATH), "users_entrance": users_entrance}


@app.get("/api/ticket/{ticket_id}")
async def read_items(ticket_id: int):
    for user in get_users_from_excel(OUTPUT_FILE_PATH):
        if user['ticket_id'] == ticket_id:
            return user
    raise HTTPException(status_code=404, detail="User Not Found")


@app.get("/reception", response_class=HTMLResponse)
async def reception_page(request: Request):
    return templates.TemplateResponse("reception.html", {"request": request,
                                                         "base_url": DOMAIN_NAME,
                                                         "page_title": PAGE_TITLE})


@app.get("/api/reception/{ticket_id}")
async def verify_ticket(ticket_id: int, password: Optional[str] = None):
    if has_permission(password):
        for user in get_users_from_excel(OUTPUT_FILE_PATH):
            if user['ticket_id'] == ticket_id:
                if ticket_id in users_entrance:
                    users_entrance[ticket_id] += 1
                else:
                    users_entrance[ticket_id] = 1

                return {
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'entrance_count': users_entrance[ticket_id]
                }


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # uvicorn.run(app)