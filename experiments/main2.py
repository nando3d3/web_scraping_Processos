from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup


app = Flask(__name__)
url =  "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"

def pesquisa_processo(data_request):
    service = Service()
    options = ChromeOptions()
    driver = webdriver.Chrome(
        service=service, options=options
    )  # inicia um driver do Chrome
    try:
        driver.get(url)  # acessa a url fornecida
        # identifica o campo de pesquisa e preenche com o CPF ou nome fornecido
        if "cpf" in data_request:
            info = data_request["cpf"]
            campo_pesquisa = driver.find_element(
                By.XPATH, '//*[@id="fPP:dnp:nomeParte"]'
            )
        elif "nome" in data_request:
            info = data_request["nome"]
            campo_pesquisa = driver.find_element(
                By.XPATH, '//*[@id="fPP:dnp:nomeParte"]'
            )
        campo_pesquisa.click()  # clica no campo de pesquisa
        campo_pesquisa.send_keys(info)  # insere o texto no campo de pesquisa
        driver.find_element(
            By.XPATH, '//*[@id="fPP:searchProcessos"]'
        ).click()  # clica no botao de pesquisa
        # aguarda ate que a tabela de resultados seja carregada na página
        WebDriverWait(driver, 200).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]')
            )
        )
        tabela = driver.find_element(
            By.XPATH, '//*[@id="fPP:processosGridPanel_body"]'
        )  # localiza a tabela de resultados
        html_tabela = tabela.get_attribute("outerHTML")  # extrai html da tabela
        return html_tabela
    finally:
        driver.quit()  # fecha o navegador apos a execucao


def format_dataframe(html_tabela):
    soup = BeautifulSoup(html_tabela, "html.parser")  # cria um objeto BeautifulSoup
    dados_tabela = []
    for linha in soup.find_all("tr"):  # Itera sobre cada linha da tabela
        dados_linha = []
        link_tag = linha.find(
            "a", class_="btn btn-default btn-sm"
        )  # Localiza o link de detalhes do processo
        if link_tag:
            link = link_tag.get("onclick").split("'")[3]
            link = "https://pje1g.trf1.jus.br" + link
        dados_linha += [
            coluna.get_text(strip=True) for coluna in linha.find_all(["th", "td"])
        ]
        if "Ver detalhes do processo" in dados_linha:
            indice = dados_linha.index("Ver detalhes do processo")
            dados_linha[indice] = link
        dados_tabela.append(dados_linha)
    df = pd.DataFrame(
        dados_tabela, columns=["link", "processo", "ultima_movimentacao"]
    )  # Cria DataFrame com os dados
    df = df.iloc[2:]
    df.reset_index(drop=True, inplace=True )
    return df


def return_json_dataframe(data_request):
    html_tabela = pesquisa_processo(data_request)
    data = format_dataframe(html_tabela)
    json_data = data.to_json(orient="records")
    return json_data


@app.route("/consulta", methods=["POST"])
def consulta_processo_post():
    data_request = request.get_json()
    df_json = return_json_dataframe(data_request)
    return df_json


app.run(port= process.env.port )
