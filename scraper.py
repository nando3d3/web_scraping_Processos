from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, nome, url):
        self.app = Flask(__name__)
        self.url = url
        self.nome = nome
    
    def pesquisa_processo(self, cpf=None, nome=None):
        service = Service()
        options = ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(self.url)
            
            if nome and not cpf:
                info = nome
                campo_pesquisa = driver.find_element(By.XPATH, '//*[@id="fPP:dnp:nomeParte"]')
            elif cpf and not nome:
                info = cpf
                campo_pesquisa = driver.find_element(By.XPATH, '//*[@id="fPP:dpDec:documentoParte"]')
            
            campo_pesquisa.click()
            campo_pesquisa.send_keys(info)
            
            driver.find_element(By.XPATH, '//*[@id="fPP:searchProcessos"]').click()
            
            WebDriverWait(driver, 200).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]'))
            )
            
            tabela = driver.find_element(By.XPATH, '//*[@id="fPP:processosGridPanel_body"]')
            html_tabela = tabela.get_attribute('outerHTML')
            
            return html_tabela
            
        finally:
            driver.quit()

    def save_csv(self, html_tabela):
        soup = BeautifulSoup(html_tabela, 'html.parser')
        
        dados_tabela = []
        for linha in soup.find_all('tr'):
            dados_linha = []
            link_tag = linha.find('a', class_='btn btn-default btn-sm')
            if link_tag:
                link = link_tag.get('onclick').split("'")[3]
                link = 'https://pje1g.trf1.jus.br' + link
            dados_linha += [coluna.get_text(strip=True) for coluna in linha.find_all(['th', 'td'])]
            if 'Ver detalhes do processo' in dados_linha:
                indice = dados_linha.index('Ver detalhes do processo')
                dados_linha[indice] = link
            dados_tabela.append(dados_linha)
        
        df = pd.DataFrame(dados_tabela, columns=['link', 'processo', 'ultima_movimentacao'])
        df = df.iloc[2:]
        df.reset_index(drop=True, inplace=True)
        
        filepath = 'lista_processos.csv'
        df.to_csv(filepath, index=False)
        return filepath
    
    def run_server(self):
        @self.app.route('/')
        def consulta_processos():
            html_tabela = self.pesquisa_processo(nome=self.nome)
            filepath = self.save_csv(html_tabela)
            df = pd.read_csv(filepath)
            return render_template('index.html', table=df.to_html())
        
        self.app.run(debug=True)