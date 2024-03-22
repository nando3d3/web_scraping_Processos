from ProcessSearcher import ProcessSearcher
import json


def main():
        dr = {
            "nome": "João Silva"
        }

        PS = ProcessSearcher(dr)
        
        json_file = PS.json_response
        
        # Nome do arquivo JSON
        nome_arquivo = "dados.json"

        # Escreve o dicionário no arquivo JSON
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write(json_file)
if __name__ == "__main__":
    main()
