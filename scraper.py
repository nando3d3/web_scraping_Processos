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
        self.service = Service()
        self.options = ChromeOptions()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.url = url
        self.nome = nome
    
    def pesquisa_processo(self, cpf = None, nome = None):
        if nome and not cpf:
            info = nome
            campo_pesquisa = self.driver.find_element(By.XPATH, '//*[@id="fPP:dnp:nomeParte"]')
        if cpf and not nome:
            info = cpf
            campo_pesquisa = self.driver.find_element(By.XPATH, '//*[@id="fPP:dpDec:documentoParte"]')
        
        campo_pesquisa.click()
        campo_pesquisa.send_keys(info)
        
        self.driver.find_element(By.XPATH, '//*[@id="fPP:searchProcessos"]').click()

    def lista_processos(self):
        WebDriverWait(self.driver, 200).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]'))
        )
        tabela = self.driver.find_element(By.XPATH, '//*[@id="fPP:processosGridPanel_body"]')
        
        html_tabela = tabela.get_attribute('outerHTML')
        soup = BeautifulSoup(html_tabela, 'html.parser')
        
        dados_tabela = []

        for linha in soup.find_all('tr'):
            dados_linha = []
            
            link_tag = linha.find('a', class_='btn btn-default btn-sm')
            if link_tag:
                link = link_tag.get('onclick').split("'")[3]  # extrai o link do atributo onclick
                link = 'https://pje1g.trf1.jus.br' + link
                
            dados_linha += [coluna.get_text(strip=True) for coluna in linha.find_all(['th', 'td'])]
            
            if 'Ver detalhes do processo' in dados_linha:
                indice = dados_linha.index('Ver detalhes do processo')
                dados_linha[indice] = link
            
            dados_tabela.append(dados_linha)
        
        df = pd.DataFrame(dados_tabela, columns=['link', 'processo', 'ultima_movimentacao'])
        df = df.iloc[2:]
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def save_csv(self, df):
        filepath = 'lista_processos.csv'
        return df.to_csv(filepath, index = False)
    
    def run_server(self):
        @self.app.route('/consulta')
        def consulta_processos():
            self.driver.get(self.url)
            self.pesquisa_processo(nome=self.nome)
            df = self.lista_processos()
            filepath = self.save_csv(df)
            self.driver.quit()
            return render_template('index.html', table=df.to_html())
        
        self.app.run(debug=True)