# Carrega libs usadas no ETL (Necessário instalar)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import datetime

# Define data de processamento
data_processamento = datetime.now().strftime('%Y-%m-%d_%Hh-%Mm-%Ss')

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')

# Inicializa o ChromeDriver
chrome_service = Service(ChromeDriverManager().install()) # Instala versão do ChromeDriver compatível com a versão do Chrome.
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Acessa o link da fonte
url = "https://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data=&Mercadoria=ETH"
driver.get(url)

meses = {
    'F': '01',
    'G': '02',
    'H': '03',
    'J': '04',
    'K': '05',
    'M': '06',
    'N': '07',
    'Q': '08',
    'U': '09',
    'V': '10',
    'X': '11',
    'Z': '12'
}

# Função para converter o contrato
def converter_contrato(contrato):
    letra = contrato[0] # Primeira letra do contrato
    ano = contrato[1:] # Restante do contrato (ano)
    mes = meses.get(letra, 'Mês inválido') # Compara contrato com dicionário de meses para formatar corretamente.
    return f'{mes}/{ano}'

# Nome do CSV com a data de processamento
nome_arquivo = (f'C:/caminho/contratos/hydrated_ethanol_{data_processamento}.csv')

# Cria e abre para edição o arquivo CSV para escrita fora do loop
with open(nome_arquivo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Data", "Contrato", "Valor BRL/Metro_Cubico"]) # Define cabeçalho do CSV

    try:
        # Aguarda até que os dados sejam carregados
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'teste'))
        )

        # Cria uma lista para armazenar os contratos
        contracts = []

        # Percorre as linhas do html do link da fonte
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            # Verifica as classes que podem ser o nome do contrato
            cells = row.find_elements(By.XPATH, ".//td[contains(@class, 'tabelaConteudo')]")
            for cell in cells:
                contracts.append(converter_contrato(cell.text.strip())) # Puxa contrato e retira espaços da str para processar corretamente na função.

        ## Exibe os contratos
        #for contract in contracts:
        #    print(contract)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    try:
        # Aguarda até que os dados sejam carregados
        mercado_fut2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'MercadoFut2'))
        )

        # Cria uma lista para armazenar os valores
        prices = []

        # Percorre as linhas do html do link da fonte
        rows = mercado_fut2.find_elements(By.TAG_NAME, 'tr')
        for row in rows[1:]:
            # Puxa o valor dos contratos
            cells = row.find_elements(By.TAG_NAME, 'td')

            # Verifica se há pelo menos 6 células, pois o valor está na sexta célula.
            if len(cells) >= 6:
                price = cells[5].text.strip().replace('.', '').replace(',', '.') # Altera vírgula para ponto, possibilitando conversão para float.
                prices.append(price)

        ## Exibe os valores
        #for value in prices:
        #    print(value)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    # Adiciona as linhas ao CSV
    for i1, i2 in zip(contracts, prices):
        writer.writerow([data_processamento, i1, i2])


# Fecha o driver
driver.quit()