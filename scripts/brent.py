# Carrega libs usadas no ETL (Necessário instalar)
import time
from datetime import datetime
import csv
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Define data de processamento
data_processamento = datetime.now().strftime('%Y-%m-%d_%Hh-%Mm-%Ss')

# Puxa a cotação do dólar:
url = "https://www.dolarhoje.com/" # Coloque a URL do site fonte.
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Identifica local onde está a cotação no site fonte:
cotacao = soup.find("input", {"id": "nacional"})
if cotacao and 'value' in cotacao.attrs:
    ctcUSD = cotacao['value'].replace(',', '.') # Troca vírgula por ponto, para possibilitar a conversão para Float.
    ctcUSD = float(ctcUSD)
    print(f"Cotação do Dólar ('{data_processamento}'): R$ {ctcUSD}") # Exibe a cotação no prompt
else:
    print("Cotação do Dólar não encontrada.") # Informa caso o Web scraping não funcionou.

# Puxa cotação dos contratos futuros de açúcar:

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# Inicializa o ChromeDriver
chrome_service = Service(ChromeDriverManager().install()) # Instala versão do ChromeDriver compatível com a versão do Chrome.
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Acessa o link da fonte
driver.get("https://www.investing.com/commodities/brent-oil-contracts")

# Espera o link da fonte carregar
time.sleep(5)

# Extrai os dados do link da fonte
rows = driver.find_elements(By.XPATH, ".//tbody/tr") # Seleciona todos os valores


meses = {
    'Jan': '01/',
    'Feb': '02/',
    'Mar': '03/',
    'Apr': '04/',
    'May': '05/',
    'Jun': '06/',
    'Jul': '07/',
    'Aug': '08/',
    'Sep': '09/',
    'Oct': '10/',
    'Nov': '11/',
    'Dec': '12/'
}

# Função para converter o contrato
def converter_contrato(contrato):
    letra = contrato[:3] # Primeira letra do contrato
    ano = contrato[3:] # Restante do contrato (ano)
    mes = meses.get(letra, 'Inválido') # Compara contrato com dicionário de meses para formatar corretamente.
    return f'{mes}{ano}'

# Nome do CSV com a data de processamento
nome_arquivo = (f'C:/caminho/contratos/brent_{data_processamento}.csv')

# Cria e abre para edição o CSV para escrita fora do loop
with open(nome_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Data", "Contrato", "Valor USD/bbl", "Valor BRL/bbl"]) # Define cabeçalho do CSV

    # Percorre cada linha e extrai o valor
    for row in rows:
        pair_id = row.get_attribute("id")

        # Trabalhando sobre a estrutura da fonte (html), verifica se o ID está no intervalo correto (evitando puxar dados fora de contexto).
        if pair_id in [f"pair_{i}" for i in range(2, 78)]:
            cells = row.find_elements(By.TAG_NAME, "td") 

            if len(cells) > 2:
                contract = cells[1].text.replace(' ', '') # Puxa o contrato
                value = cells[2].text # Puxa o valor

                try:
                    contract = converter_contrato(contract).replace(' ', '') # Retira espaços da str para processar corretamente na função.
                except IndexError:
                    print(f"Erro ao tratar o contrato '{contract}'.")

                # Converte o valor para float
                try:
                    priceUSD = float(value.strip()[:5].replace(',', '.')) # Altera vírgula para ponto, possibilitando conversão para float.
                    priceBRL = priceUSD * ctcUSD
                except ValueError:
                    print(f"Erro ao converter o valor '{value}' para float.")
                    continue # Pula para o próximo valor se houver erro

                # Adiciona as linhas ao CSV
                writer.writerow([data_processamento, contract, priceUSD, priceBRL])
                
                # Exibe cada linha adiciona. OBS: Comentei pra deixar execução mais fluída.
                #print(f"Contrato: {contract} - USD: {priceUSD} - (BRL): {priceBRL}", end = '\n\n')
            else:
                print("Linha não contém células suficientes.")

# Fecha o driver
driver.quit()


