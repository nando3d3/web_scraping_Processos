from fastapi import FastAPI, Request
import uvicorn
from ProcessSearcher import ProcessSearcher

app = FastAPI()

@app.post("/")
async def search_process(request: Request):
    data_request = (
        await request.json()
    )
    data_response = ProcessSearcher(data_request)
    return data_response.json_response

if __name__ == "__main__":
    print("Pressione CTRC + C para fechar...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
