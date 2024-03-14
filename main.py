from fastapi import FastAPI

from fastapi import FastAPI, Request
import json
from ProcessSearcher import ProcessSearcher


app = FastAPI()


@app.post("/")
async def search_process(request: Request):

    data_request = (
        await request.json()
    )  # Obter os dados enviados no corpo da solicitação
    data_response = ProcessSearcher(data_request)
    print(data_request)
    return data_response.json_response
