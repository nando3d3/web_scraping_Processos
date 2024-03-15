from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ProcessSearcher import ProcessSearcher
#from configNgrok import start_ngrok_with_token

#start_ngrok_with_token()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere '*' para a origem desejada ou deixe como está para permitir todas as origens
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Métodos HTTP permitidos
    allow_headers=["*"],  # Headers permitidos
)

@app.post("/")
async def search_process(request: Request):
    data_request = (
        await request.json()
    )
    data_response = ProcessSearcher(data_request)
    return data_response.json_response

if __name__ == "__main__":
    print("Pressione CTRC + C para fechar...")
    uvicorn.run(app, port=8000)
