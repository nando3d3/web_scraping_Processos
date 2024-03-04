from Cors import App
from flask import request
import json
from ProcessSearcher import ProcessSearcher

data = []


# modified
@App.route("/", methods=["POST"])
def search_process():

    data_request = request.get_json()
    print("recebendo data_request")
    print(data_request)
    data_response = ProcessSearcher(data_request)
    return data_response.json_response
