"""
Script automatizado para extrair TODOS os livros do https://books.toscrape.com/
Gera um CSV com campos: Título, Categoria, Preço, Rating, Disponibilidade, Imagem

Como executar:
python scripts/scraper_books.py

Dependências: requests, beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv
import os

BASE_URL = "https://books.toscrape.com/"
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
CSV_PATH = os.path.join(DATA_DIR, 'livros_completo.csv')

def get_soup(url):
    """
    Faz a conexão com a página e devolve o HTML formatado para o BeautifulSoup.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return BeautifulSoup(resp.text, 'html.parser')

def extrair_livros_da_pagina(soup):
    """
    Lê os dados dos livros na página (título, preço, rating etc.).
    """
    livros = []
    for livro in soup.select('article.product_pod'):
        titulo = livro.h3.a['title'].strip()
        preco = livro.select_one('.price_color').text.strip().replace('£', '').replace('Â', '').replace(',', '.')
        rating = livro.p['class'][1]  # Ex: "Three"
        disponibilidade = livro.select_one('.instock.availability').text.strip()
        url_imagem = BASE_URL + livro.find('img')['src'].replace('../', '')

        detalhe_href = livro.h3.a['href']
        detalhe_url = BASE_URL + 'catalogue/' + detalhe_href.split('/')[-2] + '/' + detalhe_href.split('/')[-1]
        detalhe_soup = get_soup(detalhe_url)
        categoria = detalhe_soup.select('ul.breadcrumb li a')[2].text.strip()

        livros.append({
            'Título': titulo,
            'Categoria': categoria,
            'Preço': preco,
            'Rating': rating,
            'Disponibilidade': disponibilidade,
            'Imagem': url_imagem,
        })
    return livros

def coletar_todos_os_livros():
    """
    Roda o scraping em todas as páginas do site.
    """
    livros = []
    proxima_pagina = 'catalogue/page-1.html'
    primeira_pagina = True

    while proxima_pagina:
        url = BASE_URL + proxima_pagina if not primeira_pagina else BASE_URL
        print(f'Raspando página: {url}')
        soup = get_soup(url)
        livros.extend(extrair_livros_da_pagina(soup))
        proxima = soup.select_one('li.next > a')
        if proxima:
            proxima_pagina = proxima['href']
            if not proxima_pagina.startswith('catalogue'):
                proxima_pagina = 'catalogue/' + proxima_pagina
            primeira_pagina = False
        else:
            break
    return livros

def salvar_csv(lista_livros, caminho_csv):
    """
    Salva a lista de livros em um arquivo CSV dentro da pasta data.
    """
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)
    with open(caminho_csv, mode='w', newline='', encoding='utf-8') as arquivo:
        campos = ['Título', 'Categoria', 'Preço', 'Rating', 'Disponibilidade', 'Imagem']
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=';')
        escritor.writeheader()
        for livro in lista_livros:
            escritor.writerow(livro)

if __name__ == "__main__":
    print("Iniciando scraping do site inteiro...")
    livros = coletar_todos_os_livros()
    salvar_csv(livros, CSV_PATH)
    print(f"Scraping finalizado: {len(livros)} livros salvos em {CSV_PATH}")
