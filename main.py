from scraper import *

def main():
    #nome = 'Débora de Oliveira'
    # nome = 'Iran Velasco Nascimento'
    api = Scraper('https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam')
    api.run_server()
    
if __name__ == "__main__":
    main()