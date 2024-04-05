from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ProcessSearcher import ProcessSearcher
from configNgrok import start_ngrok_with_token
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    # Altere '*' para a origem desejada ou deixe como está para permitir todas as origens
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],  # Métodos HTTP permitidos
    allow_headers=["*"],  # Headers permitidos
)


@app.post("/")
async def search_process(request: Request):
    data_request = (
        await request.json()
    )
    data_response = ProcessSearcher(data_request)
    return data_response.json_response


@app.post("/html")
async def get_html(request: Request):
    data_request = (
        await request.json()
    )
    data_response = ProcessSearcher(data_request)

    return templates.TemplateResponse("index.html", {"request": request, "name": "retornando diferente", "data": data_response})


if __name__ == "__main__":
    try:
        # start_ngrok_with_token()
        print("Pressione CTRC + C para fechar...")
        uvicorn.run(app, port=1344)
    except Exception as e:
        print(f'erro ao iniciar:\n {e}')
