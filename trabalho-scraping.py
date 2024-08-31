import re
import csv
from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime

def get_html_content(url):
    try:
        with urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def extract_info(soup, row_id):
    row = soup.find('tr', id=row_id)
    if row:
        return row.find('td', class_='w2p_fw').text.strip()
    return ''

def get_neighbour_names(soup, base_url):
    neighbours_row = soup.find('tr', id='places_neighbours__row')
    if neighbours_row:
        neighbour_links = neighbours_row.find_all('a')
        neighbour_names = []
        for link in neighbour_links:
            neighbour_url = urljoin(base_url, link['href'])
            neighbour_html = get_html_content(neighbour_url)
            if neighbour_html:
                neighbour_soup = BeautifulSoup(neighbour_html, 'html.parser')
                neighbour_name = extract_info(neighbour_soup, 'places_country__row')
                if neighbour_name:
                    neighbour_names.append(neighbour_name)
        return ', '.join(neighbour_names)
    return ''

def process_page(url, base_url, data):
    html = get_html_content(url)
    if html:
        bs = BeautifulSoup(html, 'html.parser')

        # Para cada link de país na página
        for link in bs.find_all('a', href=re.compile(r'view', re.IGNORECASE)):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            print(f"\nProcessando país: {link.text.strip()}")
            
            # Obtém o conteúdo HTML da página do país
            country_html = get_html_content(full_url)
            if country_html:
                country_bs = BeautifulSoup(country_html, 'html.parser')
                
                # Extrai as informações
                country = extract_info(country_bs, 'places_country__row')
                currency_name = extract_info(country_bs, 'places_currency_name__row')
                continent = extract_info(country_bs, 'places_continent__row')
                neighbours = get_neighbour_names(country_bs, base_url)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Adiciona os dados à lista
                data.append([country, currency_name, continent, neighbours, timestamp])
                
                print(f"Dados extraídos para: {country}")
                print(f"Vizinhos: {neighbours}")
            
            print("-" * 50)

        # Procura o link "NEXT"
        next_link = bs.find('a', string=lambda text: text and 'Next' in text)
        if next_link:
            next_url = urljoin(url, next_link['href'])
            print(f"Próxima página: {next_url}")
            return next_url
        else:
            print("Não há mais páginas para processar.")
            return None
    return None

# URL base - INICIO DO CODIGO
base_url = 'http://127.0.0.1:8000/places/default/index'

# Lista para armazenar os dados
data = [['country', 'currency_name', 'continent', 'neighbours', 'timestamp']]

# Processa todas as páginas
current_url = base_url
while current_url:
    print(f"Processando página: {current_url}")
    current_url = process_page(current_url, base_url, data)

# Salva os dados em um arquivo CSV
csv_filename = 'countries_data.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(data)

print(f"\nDados salvos em {csv_filename}")