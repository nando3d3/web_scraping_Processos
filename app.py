from typing import Optional
from fastapi import FastAPI, Request, Form
import uvicorn
from ProcessSearcher import ProcessSearcher
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import webbrowser

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# captura resultado da pesquisa e realiza web scrap


@app.post("/result")
async def search_process(request: Request, pesquisa: str = Form(...), tipo_pesquisa: str = Form(...)):
    data_request = {tipo_pesquisa: pesquisa}
    print(str(data_request))
    data_response = ProcessSearcher(data_request).table_response
    # retorna página de resultados formatada
    return templates.TemplateResponse("resultado.html", {"request": request, "pesquisa": pesquisa, "resultado": data_response})
# Renderiza pagina de pesquisa


@app.get("/", response_class=HTMLResponse)
async def pesquisa_page(request: Request):

    return templates.TemplateResponse("pesquisa.html", {"request": request})

# DIGITE uvicorn app:app --reload para executar

if __name__ == "__main__":
    try:
        # webbrowser.open_new_tab('http://localhost:1344')
        webbrowser.open_new_tab('http://127.0.0.1:1344/')
        uvicorn.run(app, port=1344)
    except Exception as e:
        print(f'erro ao iniciar:\n {e}')
