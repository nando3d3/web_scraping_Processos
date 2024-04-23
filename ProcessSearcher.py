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

class ProcessSearcher:
    def __init__(self, data_request):
        service = Service()
        options = ChromeOptions()
        options.add_argument("--no-sandbox")  # desativa o sandbox
        #options.add_argument("--headless") #executa sem GUI
        # desabilita aceleracao de hardware
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options, service)
        self.data_request = data_request

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
        
        #eproc
        trf2 = ["https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica"]

        tables_dict = {}

        tables_dict['trf1'] = self._search_pje(trf1[0], trf1[1])
        tables_dict['trf3'] = self._search_pje(trf3[0], trf3[1])
        tables_dict["trf6"] = self._search_pje(trf6[0], trf6[1])
        tables_dict['cnj'] = self._search_pje(cnj[0], cnj[1])
        tables_dict['stf'] = self._search_stf(stf[1])
        tables_dict['trf2'] = self._search_eproc(trf2[0])
        self.driver.quit()

        self.table_response = self.format_html_table(tables_dict)

    # Formata o dicionário, transformando os df em tabelas e colocando titulo
    def format_html_table(self, tables_dict):
        html_tables = ""
        for title, df in tables_dict.items():
            if df is not None:
                if not df.empty:
                    df = self.transform_to_links(df)

                    html_tables += f"<h2>{title.upper()}</h2>\n"
                    html_tables += df.to_html(index=False, escape=False)
        
        return html_tables

    # transforma columa de processo em hyperlink
    def transform_to_links(self, df: pd.DataFrame) -> pd.DataFrame:
        def make_link(row):
            return f'<a href="{row["link"]}"  target="_blank">{row["ultima_movimentacao"]}</a>'

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
                info = info[:3] + '.' + info[3:6] + '.' + info[6:9] + '-' + info[9:]
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
                return pd.Dataframe(columns = ['link','processo', 'ultima_movimentacao'])
            elif "nome" in dr:
                info = dr["nome"].upper()
            
            info_quote = quote(info)
            
            url_pesquisa = link + info_quote
            self.driver.get(url_pesquisa)
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="quantidade"]')))
            
            qtde_processo = self.driver.find_element(By.XPATH, '//*[@id="quantidade"]').text
            qtde_processo = min(int(qtde_processo), 20)
            
            return self._format_dataframe_stf(qtde_processo, info)
            
            
        except Exception as e:
            print(e.with_traceback)

    def _format_dataframe_stf(self, qtde_processo, nome):
        nome = self.remover_acentos(nome)
        
        partes = {"link": [], "processo": [], "ultima_movimentacao": []}

        
        for i in range(1, qtde_processo+1):
            nome_parte = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[2]/div/div[1]/div[2]').text
            nome_parte = self.remover_acentos(nome_parte)
            
            if nome_parte == nome:
                link = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[1]/h6[1]/span/a').get_attribute('href')

                processo = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[1]/h6[1]/span/a').text
                
                ult_mov = self.driver.find_element(By.XPATH, f'//*[@id="card_processos"]/div[{i}]/div[2]/div/div[2]/div[2]').text
                partes["link"].append(link)
                partes["processo"].append(processo)
                partes["ultima_movimentacao"].append(ult_mov)
        return pd.DataFrame.from_dict(partes)
    
    def _search_eproc(self, url):
        
        try:
            self.driver.get(url)
            
            dr = self.data_request
            if "cpf" in dr:
                search_field = self.driver.find_element(
                        By.XPATH, '//*[@id="txtCpfCnpj"]'
                    )
            elif "nome" in dr:
                search_field = self.driver.find_element(
                        By.XPATH, '//*[@id="txtStrParte"]' 
                    )
            info = list(dr.values())[0]
            search_field.click()
            search_field.send_keys(info)
            
            #consulta
            self.driver.find_element(
                By.XPATH, '//*[@id="sbmNovo"]'
            ).click()
            
            #espera tabela de resultados
            WebDriverWait(self.driver, 70).until (
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="divInfraAreaTabela"]/table')
                    )
                )

            return self._parse_results()
        
        except Exception as e:
            print(e.with_traceback)
        
    def _parse_results(self):
        
        linhas = self.driver.find_elements(By.XPATH, '//*[@id="divInfraAreaTabela"]/table/tbody/tr')
        tam_tabela = len(linhas) + 1
        dr = self.data_request
        if "nome" in dr:
            nome = dr["nome"]
            dfs = []
            for i in range(2, tam_tabela):
                    xpath_nomeParte = f'//*[@id="divInfraAreaTabela"]/table/tbody/tr[{i}]/td[1]'
                    nome_parte = self.driver.find_element(By.XPATH, xpath_nomeParte).text
                    
                    if self.remover_acentos(nome_parte).lower() == self.remover_acentos(nome).lower():
                        link_processos = self.driver.find_element(By.XPATH, f'{xpath_nomeParte}/a').get_attribute("href")
                        
                        #abrir link com processos
                        self.driver.execute_script("window.open();")
                        
                        #muda para nova aba
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        
                        # entra no link de processes
                        self.driver.get(link_processos)

                        dfs.append(self._info_processos())
                        
                        #retorna para aba principal
                        self.driver.switch_to.window(self.driver.window_handles[0])
            
            return pd.concat(dfs, ignore_index=True)
                
        return self._info_processos()
                   
    def _info_processos(self):
        partes = {"link": [], "processo": [], "ultima_movimentacao": []}
        
        #informacoes sobre processo
        table_processos = self.driver.find_element(By.XPATH, '//*[@id="divInfraAreaTabela"]/table/tbody')
        qtde_processos = len(table_processos.find_elements(By.TAG_NAME, 'tr'))
        
        for i in range(2, qtde_processos):
            link = self.driver.find_element(By.XPATH, f'//*[@id="divInfraAreaTabela"]/table/tbody/tr[{i}]/td[1]/a').get_attribute("href")
            processo = self.driver.find_element(By.XPATH, f'//*[@id="divInfraAreaTabela"]/table/tbody/tr[{i}]/td[1]').text
            ult_mov =  self.driver.find_element(By.XPATH, f'//*[@id="divInfraAreaTabela"]/table/tbody/tr[{i}]/td[5]').text
            
            partes["link"].append(link)
            partes["processo"].append(processo)
            
            if ult_mov == '':
                ult_mov = 'Acessar Processo'
            
            partes["ultima_movimentacao"].append(ult_mov)

        return pd.DataFrame.from_dict(partes)
                
    def remover_acentos(self, texto):
        texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        
        return texto_sem_acentos