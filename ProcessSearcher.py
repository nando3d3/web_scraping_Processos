from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import json


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

        trf1 = ["https://pje1g.trf1.jus.br",
                "https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam"]
        trf3 = ["https://pje1g.trf3.jus.br",
                "https://pje1g.trf3.jus.br/pje/ConsultaPublica/listView.seam"]
        trf6 = ["https://pje1g.trf6.jus.br",
                "https://pje1g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam"]
        cnj = ["https://www.cnj.jus.br",
               "https://www.cnj.jus.br/pjecnj/ConsultaPublica/listView.seam"]

        tables_dict = {}

        tables_dict['trf1'] = self._search_pje_trf(trf1[0], trf1[1])
        tables_dict['trf3'] = self._search_pje_trf(trf3[0], trf3[1])
        tables_dict["trf6"] = self._search_pje_trf(trf6[0], trf6[1])
        tables_dict['cnj'] = self._search_pje_trf(cnj[0], cnj[1])
        self.driver.quit()
        
        
        self.table_response = self.format_html_table(tables_dict)

    #Formata o dicionário, transformando os df em tabelas e colocando titulo
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
        df = df.rename(columns={'processo': 'Processo', 'ultima_movimentacao': 'Última Movimentação'})
        return df
        
    def _search_pje_trf(self, link, url):

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

            return self._format_dataframe_pje_df(html_table, link)

        except Exception as e:
            print(e.with_traceback)

    def _format_dataframe_pje_df(self, html_table, link_trf):
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

    # Funções para outros sites
    # ...
