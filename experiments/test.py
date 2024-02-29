from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/', methods=['GET'])
def get_items():
    data = {
        "items": [
            {
                "link": "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam?ca=8d7bcea504319ff5441092ef6cef780c7ac7bfa1300bdd79",
                "processo": "CUMPRIMENTO DE SENTENÇACumSen 0039504-91.2004.4.01.3400 - Abono Pecuniário (Art. 78 Lei 8.112/1990)UNIAO FEDERAL (FAZENDA NACIONAL) X AJUFER ASSOCIACAO DOS JUIZES FEDERAIS DA 1A REGIAO e outros (23)",
                "ultima_movimentacao": "Juntada de certidão (01/08/2022 16:27:12)"
            }
        ]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
