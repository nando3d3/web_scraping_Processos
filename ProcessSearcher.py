from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import unicodedata
from urllib.parse import quote
import pandas as pd
import json
from time import sleep

class ProcessSearcher:
    def __init__(self, data_request):
        service = Service()
        options = ChromeOptions()
        options.add_argument("--no-sandbox")  # desativa o sandbox
        # options.add_argument("--headless") #executa sem GUI
        # desabilita aceleracao de hardware
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options, service)
        self.data_request = data_request
        self.df = pd.DataFrame(
            columns=["link", "processo", "ultima_movimentacao"])

        #pje
        trf1 = ["https://pje1g.trf1.jus.br",
                "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"]
        trf3 = ["https://pje1g.trf3.jus.br",
                "https://pje1g.trf3.jus.br/pje/ConsultaPublica/listView.seam"]
        trf6 = ["https://pje1g.trf6.jus.br",
                "https://pje1g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam"]
        cnj = ["https://www.cnj.jus.br",
               "https://www.cnj.jus.br/pjecnj/ConsultaPublica/listView.seam"]
        
        #site stf
        stf = ["https://portal.stf.jus.br/processos/", "https://portal.stf.jus.br/processos/listarPartes.asp?termo="]
        

        tables_dict = {}

        # tables_dict['trf1'] = self._search_pje(trf1[0], trf1[1])
        # tables_dict['trf3'] = self._search_pje(trf3[0], trf3[1])
        # tables_dict["trf6"] = self._search_pje(trf6[0], trf6[1])
        # tables_dict['cnj'] = self._search_pje(cnj[0], cnj[1])
        self._search_stf(stf[1])
        self.driver.quit()

        self.table_response = self.format_html_table(tables_dict)

    # Formata o dicionário, transformando os df em tabelas e colocando titulo
    def format_html_table(self, tables_dict):
        html_tables = ""
        for title, df in tables_dict.items():
            if df is not None:
                df = self.transform_to_links(df)

                html_tables += f"<h2>{title.upper()}</h2>\n"
                html_tables += df.to_html(index=False, escape=False)
        return html_tables

    # transforma columa de processo em hyperlink
    def transform_to_links(self, df: pd.DataFrame) -> pd.DataFrame:
        def make_link(row):
            return f'<a href="{row["link"]}"  target="_blank">{row["processo"]}</a>'

        df['ultima_movimentacao'] = df.apply(make_link, axis=1)
        df.drop(columns=['link'], inplace=True)
        df = df.rename(columns={'processo': 'Processo',
                       'ultima_movimentacao': 'Última Movimentação'})
        return df

    def _search_pje(self, link, url):

        try:
            self.driver.get(url)

            dr = self.data_request
            if "cpf" in dr:
                info = dr["cpf"]
                search_field = self.driver.find_element(
                    By.XPATH, '//*[@id="fPP:dpDec:documentoParte"]'
                )
            elif "nome" in dr:
                info = dr["nome"]
                search_field = self.driver.find_element(
                    By.XPATH, '//*[@id="fPP:dnp:nomeParte"]'
                )

            search_field.click()
            search_field.send_keys(info)

            # clica botao de pesquisa
            self.driver.find_element(
                By.XPATH, '//*[@id="fPP:searchProcessos"]').click()

            # wait result table

            WebDriverWait(self.driver, 100).until(
                EC.any_of(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]')),
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="fPP:j_id229"]/dt')),
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="fPP:j_id224"]/dt')),
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="fPP:j_id219"]/dt')),
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="fPP:j_id230"]/dt'))
                )
            )

            # WebDriverWait(self.driver, 70).until (
            #     EC.visibility_of_element_located(
            #         (By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]')
            #     )
            # )

            # localiza tabela e extrai html
            table = self.driver.find_element(
                By.XPATH, '//*[@id="fPP:processosGridPanel_body"]'
            )
            html_table = table.get_attribute("outerHTML")

            return self._format_dataframe_pje(html_table, link)

        except Exception as e:
            print(e.with_traceback)

    def _format_dataframe_pje(self, html_table, link_trf):
        soup = BeautifulSoup(html_table, "html.parser")

        table_data = []
        for line in soup.find_all("tr"):
            line_data = []
            link_tag = line.find(
                "a", class_="btn btn-default btn-sm"
            )  # localiza link em "detalhes do processo"

            if link_tag:
                link = link_tag.get("onclick").split("'")[3]
                link = str(link_trf) + link
            line_data += [
                column.get_text(strip=True) for column in line.find_all(["th", "td"])
            ]

            if "Ver detalhes do processo" in line_data:
                index_line = line_data.index("Ver detalhes do processo")
                line_data[index_line] = link

            table_data.append(line_data)
        df_pje = pd.DataFrame(
            table_data, columns=["link", "processo", "ultima_movimentacao"]
        )
        df_pje = df_pje.iloc[2:]
        df_pje.reset_index(drop=True, inplace=True)
        return df_pje

    def _search_stf(self, link):
        try:
            dr = self.data_request
            if "cpf" in dr:
                return 'erro'
            elif "nome" in dr:
                info = dr["nome"]
                
            info_quote = quote(info)
            
            url_pesquisa = link + info_quote
            
            self.driver.get(url_pesquisa)
            
            qtde_processo = self.driver.find_element(By.XPATH, '//*[@id="quantidade"]').text
            qtde_processo = int(qtde_processo)
            #sleep(10)
            self._format_dataframe_stf(qtde_processo, info)
            
            
        except Exception as e:
            print(e.with_traceback)

    def _format_dataframe_stf(self, qtde_processo, nome):
        nome = self.remover_acentos(nome)
        
        df_stf = pd.DataFrame(
            columns=["link", "processo", "ultima_movimentacao"]
        )
        
        
        for i in range(1, qtde_processo+1):
            nome_parte = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[2]/div/div[1]/div[2]').text
            nome_parte = self.remover_acentos(nome_parte)
            
            df_stf = pd.DataFrame(
                columns=["link", "processo", "ultima_movimentacao"]
            )
            if nome_parte == nome:
                link = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[1]/h6[1]/span/a').get_attribute('href')
                print(link + '\n')

                processo = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[1]/h6[1]/span/a').text
                print(processo + '\n')
                # ult_mov = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[2]/div/div[2]/div[2]').text
                
                # partes = {"link": link, "processo": processo, "ultima_movimentacao": ult_mov}
                
                # df_stf = df_stf.append(partes, ignore_index = True)
        
                print(partes)
                
    def remover_acentos(self, texto):
        texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        
        return texto_sem_acentos

def main():
    PS = ProcessSearcher({'nome': 'JOÃO SILVA NETO'})

main()