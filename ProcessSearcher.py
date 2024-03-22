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
        #options.add_argument("--headless") #executa sem GUI
        options.add_argument("--disable-gpu")  # desabilita aceleracao de hardware
        self.driver = webdriver.Chrome(options, service)
        self.data_request = data_request
        self.df = pd.DataFrame(columns=["link", "processo", "ultima_movimentacao"])

        trf1  = ["https://pje1g.trf1.jus.br","https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam" ,"trf1" ]
        trf3 = "https://pje1g.trf3.jus.br/pje","https://pje1g.trf3.jus.br/pje/ConsultaPublica/listView.seam", "trf3"
        trf6 = ["https://pje1g.trf6.jus.br", "https://pje1g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam", "trf6"]
        cnj = ["https://www.cnj.jus.br/pjecnj","https://www.cnj.jus.br/pjecnj/ConsultaPublica/listView.seam", "cnj"]

        json_list = []


        try:
            json_list.append(self._search_pje_trf(cnj[0], cnj[1],cnj[2]))
            json_list.append(self._search_pje_trf(trf1[0], trf1[1], trf1[2]))
            json_list.append(self._search_pje_trf(trf3[0], trf3[1], trf3[2]))
            json_list.append(self._search_pje_trf(trf6[0], trf6[1], trf6[2]))
            self.driver.quit()
    
            self.concatenar_jsons(json_list)
             
            
        except Exception as e:
            print(e.with_traceback)
        
    def concatenar_jsons(self, jsons):
        print("--------------------------------")
        print("iniciando concatenação dos jsons")
        resultado = {}

        for json_str in jsons:
            # Converte o JSON para dicionário
            json_dict = json.loads(json_str)

            resultado.update(json_dict)
            
        json_concatenado = json.dumps(resultado)
        print(json_concatenado)
        # adcionar verificação para n tentar somar json nulos, evita erro e tambem avisa caso a concatenaçao dos jsons seja nula
        # vai mostrar que nao houve pesquisas para nenhum tribunal dado o nome informado.
        return json_concatenado 
                 

    def _search_pje_trf(self, link, url, nome_trf):
        print("iniciando pesquisa no: "+str(url))


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
            self.driver.find_element(By.XPATH, '//*[@id="fPP:searchProcessos"]').click()

            # wait result table
            
            
            WebDriverWait(self.driver, 60).until(
            EC.any_of(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr[1]')),
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:j_id229"]/dt')),
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:j_id224"]/dt')),
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:j_id219"]/dt')),
                EC.visibility_of_element_located((By.XPATH, '//*[@id="fPP:j_id230"]/dt'))
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

            df_formated = self._format_dataframe_pje_df(html_table, link)
              
            return self._return_json_dataframe(df_formated, nome_trf)

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

    def _return_json_dataframe(self, df, nome_trf):
        try:
            json_data = df.to_json(orient="records")
            json_data = {nome_trf: json_data}
            json_object = json.dumps(json_data)
            print("json from dataframe: "+str(json_object))
        
            return json_object
        except Exception as e:
            print(e)
