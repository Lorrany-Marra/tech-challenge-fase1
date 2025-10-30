"""
API RESTful de livros - Tech Challenge FIAP
Implementada em FastAPI, alimentada pelo CSV gerado no scraping.
"""

import os
import csv
import logging
import time
from datetime import datetime, timedelta
from collections import Counter
from fastapi import FastAPI, HTTPException, Query, Depends, Request, Path, Form, Header, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from jose import jwt, JWTError
from pydantic import BaseModel
from unidecode import unidecode
from pythonjsonlogger import jsonlogger 


class LivroFeatures(BaseModel):
    titulo: str
    categoria: str
    preco: float
    rating: str
    disponibilidade: str

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

fileHandler = logging.FileHandler("logs_api.json")
fileHandler.setFormatter(formatter)  
logger.addHandler(fileHandler)


app = FastAPI(title="Tech Challenge FIAP - Books API", version="1.0")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed_time = (time.time() - start_time) * 1000  # em ms

    logger.info({
        "endpoint": request.url.path,
        "method": request.method,
        "ip": request.client.host,
        "status_code": response.status_code,
        "response_time_ms": round(elapsed_time, 2)
    })
    response.headers["X-Response-Time-ms"] = str(round(elapsed_time, 2))
    return response

SECRET_KEY = "sua_chave_secreta_mega_ultra_segura"  # Troque para uma mais segura no deploy!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

fake_user = {
    "username": "admin",
    "password": "admin123"
}

def autenticar_usuario(username: str, password: str):
    return username == fake_user["username"] and password == fake_user["password"]

def criar_token_acesso(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post(
    "/api/v1/auth/login",
    summary="Obter token JWT",
    description="Realiza autenticação e devolve token JWT de acesso."
)
def login(
    username: str = Form(..., description="Usuário"),
    password: str = Form(..., description="Senha"),
    request: Request = None
):
    logger.info(f"POST /api/v1/auth/login chamado por IP: {request.client.host}")
    if not autenticar_usuario(username, password):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    access_token = criar_token_acesso({"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post(
    "/api/v1/auth/refresh",
    summary="Renovar token JWT",
    description="Renova o token JWT de acesso utilizando o token anterior válido."
)
def refresh_token(
    token: str = Depends(oauth2_scheme),
    request: Request = None
):
    """
    Renova o token JWT de acesso utilizando o token anterior válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        novo_token = criar_token_acesso({"sub": username})
        return {"access_token": novo_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@app.post(
    "/api/v1/scraping/trigger",
    summary="Disparar scraping manualmente (apenas admin)",
    description="Dispara manualmente a rotina de scraping de livros (apenas para usuário admin)."
)
def trigger_scraping(
    token: str = Depends(oauth2_scheme),
    request: Request = None
):
    logger.info(f"POST /api/v1/scraping/trigger chamado por IP: {request.client.host if request else 'indefinido'}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != "admin":
            raise HTTPException(status_code=403, detail="Sem permissão")
        # resultado = rodar_scraping()
        return {"status": "Scraping de livros disparado!"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

CSV_PATH = os.path.join(os.path.dirname(__file__), '../data/livros_completo.csv')

def carregar_livros():
    """
    Lê os dados do CSV e devolve uma lista de dicionários, um por livro.
    """
    livros = []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}
            livros.append(row)
    return livros

@app.get(
    "/api/v1/books",
    summary="Lista todos os livros disponíveis",
    description="Retorna uma lista completa de todos os livros cadastrados na base de dados (extraídos do arquivo CSV)."
)
def listar_livros(request: Request):
    """
    Endpoint que retorna todos os livros cadastrados no sistema.
    Ideal para listagens completas e integração com visualização de catálogo.
    """
    logger.info(f"GET /api/v1/books chamado por IP: {request.client.host}")
    return carregar_livros()

@app.get(
    "/api/v1/books/{id:int}",
    summary="Detalhes de um livro pelo ID",
    description="Procura e retorna um livro pelo índice da lista (0 = primeiro livro). Se não achar, retorna um erro 404."
)
def detalhe_livro(
    id: int = Path(..., description="Índice do livro na lista (0 é o primeiro livro)"),
    request: Request = None
):
    logger.info(f"GET /api/v1/books/{id} chamado por IP: {request.client.host}")
    """
    Procura e retorna um livro pelo índice da lista (0 = primeiro livro).
    Se não achar, retorna um erro 404.
    """
    livros = carregar_livros()
    if 0 <= id < len(livros):
        return livros[id]
    raise HTTPException(status_code=404, detail="Livro não encontrado")

@app.get(
    "/api/v1/books/search",
    summary="Busca livros por título e/ou categoria",
    description="Permite buscar livros utilizando parte do título e/ou o nome exato da categoria. Muito útil para filtros dinâmicos e buscas combinadas."
)
def buscar_livros(
    title: Optional[str] = Query(
        None, 
        description="Parte do título do livro (não diferencia maiúsculas/minúsculas). Exemplo de uso: 'potter' localiza 'Harry Potter'."
    ),
    category: Optional[str] = Query(
        None, 
        description="Nome exato da categoria desejada, conforme está no registro. Exemplo: 'Fiction', 'Poetry', etc."
    ),
    request: Request = None
):
    """
    Filtra livros pelo título e categoria, com tratamento de erro para campos faltantes.
    """
    logger.info(f"GET /api/v1/books/search chamado por IP: {request.client.host if request else 'indefinido'}")
    livros = carregar_livros()
    resultados = []
    busca_title = title.lower().strip() if title else None
    busca_category = category.lower().strip() if category else None

    for livro in livros:
        livro_titulo = ""
        livro_categoria = ""
        for k in livro.keys():
            if k.strip().lower().replace("ã", "a").replace("í", "i").replace("ú", "u").replace("â", "a").replace("ô", "o").replace("é", "e").replace("ê", "e") == "titulo":
                livro_titulo = livro[k].strip().lower()
            if k.strip().lower().replace("ã", "a") == "categoria":
                livro_categoria = livro[k].strip().lower()
        cond_titulo = (busca_title in livro_titulo) if busca_title else True
        cond_categoria = (livro_categoria == busca_category) if busca_category else True
        if cond_titulo and cond_categoria:
            resultados.append(livro)
    if not resultados:
        raise HTTPException(
            status_code=404,
            detail="Nenhum livro encontrado com esses parâmetros."
        )
    return resultados

@app.get(
    "/api/v1/categories",
    summary="Lista todas as categorias únicas",
    description="Retorna uma lista com todas as categorias encontradas nos livros, sem repetições."
)
def listar_categorias(request: Request):
    """
    Endpoint que extrai e retorna todas as categorias únicas presentes no dataset de livros.
    Recomendada para gerar filtros dinâmicos e apoiar análises estatísticas.
    """
    logger.info(f"GET /api/v1/categories chamado por IP: {request.client.host}")
    livros = carregar_livros()
    categorias = sorted(set(livro["Categoria"] for livro in livros))
    return categorias

@app.get(
    "/api/v1/health",
    summary="Verifica saúde da API e dados",
    description=(
        "Endpoint de verificação que testa se a API está executando corretamente. "
    )
)
def health_check(request: Request):
    """
    Verifica a disponibilidade da API e do arquivo de dados.
    Retorna status e quantidade de registros para monitoramento automatizado.
    """
    logger.info(f"GET /api/v1/health chamado por IP: {request.client.host}")
    try:
        livros = carregar_livros()
        return {"status": "ok", "qtd_livros": len(livros)}
    except Exception:
        raise HTTPException(status_code=500, detail="Erro nos dados ou na API")

@app.get(
    "/api/v1/stats/overview",
    summary="Estatísticas gerais da coleção de livros",
    description=(
        "Retorna estatísticas da base de livros: Total de registros, preço médio e distribuição das avaliações (ratings). "     
    )
)
def stats_overview(request: Request):
    """
    Endpoint para obter métricas agregadas dos livros.
    Retorna total de itens, preço médio e a distribuição dos ratings.
    """
    logger.info(f"GET /api/v1/stats/overview chamado por IP: {request.client.host}")
    livros = carregar_livros()
    total = len(livros)
    precos = [float(livro.get("Preço", "0")) for livro in livros if livro.get("Preço", "").replace('.', '', 1).isdigit()]
    ratings = [livro.get("Rating", "Unknown") for livro in livros]
    media_preco = round(sum(precos) / len(precos), 2) if precos else 0
    dist_ratings = dict(Counter(ratings))
    return {
        "total_livros": total,
        "preco_medio": media_preco,
        "distribuicao_ratings": dist_ratings
    }

@app.get(
    "/api/v1/stats/categories",
    summary="Estatísticas detalhadas por categoria",
    description=(
        "Retorna, para cada categoria de livro encontrada, a quantidade de títulos e o preço médio associado. "
    )
)
def stats_categorias(request: Request):
    """
    Endpoint para obter estatísticas segmentadas por categoria.
    Devolve lista com nome da categoria, total de livros e preço médio por grupo.
    """
    logger.info(f"GET /api/v1/stats/categories chamado por IP: {request.client.host}")
    livros = carregar_livros()
    stats = {}
    for livro in livros:
        cat = ""
        for k in livro.keys():
            if k.strip().lower().replace("ã", "a") == "categoria":
                cat = livro[k]
        preco = float(livro.get("Preço", "0")) if livro.get("Preço", "").replace('.', '', 1).isdigit() else 0
        if not cat:
            continue
        if cat not in stats:
            stats[cat] = {"qtd": 0, "soma_precos": 0.0}
        stats[cat]["qtd"] += 1
        stats[cat]["soma_precos"] += preco
    result = []
    for cat, v in stats.items():
        media = round(v["soma_precos"]/v["qtd"], 2) if v["qtd"] else 0
        result.append({"categoria": cat, "qtd_livros": v["qtd"], "preco_medio": media})
    return sorted(result, key=lambda x: x["categoria"])

@app.get(
    "/api/v1/books/top-rated",
    summary="Lista livros com melhor avaliação",
    description=(
        "Retorna todos os livros com o maior rating existente na base de dados. "
    )
)
def livros_top_rated(request: Request):
    """
    Endpoint para listar todos os livros com a nota máxima. 
    Retorna uma lista detalhada dos livros top de rating do dataset.
    """
    logger.info(f"GET /api/v1/books/top-rated chamado por IP: {request.client.host}")
    livros = carregar_livros()
    ratings_convertidos = []
    for livro in livros:
        r = livro.get("Rating", "0")
        try:
            mapeamento = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            if r.strip().isdigit():
                rating_num = int(r)
            else:
                rating_num = mapeamento.get(r.lower(), 0)
            ratings_convertidos.append(rating_num)
        except:
            ratings_convertidos.append(0)
    if not ratings_convertidos:
        return []
    max_rating = max(ratings_convertidos)
    resultado = []
    for i, livro in enumerate(livros):
        r = livro.get("Rating", "0")
        mapeamento = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        rating_num = mapeamento.get(str(r).lower(), 0) if not str(r).isdigit() else int(r)
        if rating_num == max_rating:
            resultado.append(livro)
    return resultado

@app.get(
    "/api/v1/books/price-range",
    summary="Filtra livros por faixa de preço",
    description="Retorna todos os livros que o preço está dentro dos valores mínimo e máximo informados. "
)
def livros_por_faixa_de_preco(
    min: float = Query(..., description="Preço mínimo"),
    max: float = Query(..., description="Preço máximo"),
    request: Request = None
):
    """
    Filtra livros cujo preço está entre os valores informados de min e max (inclusive).
    """
    logger.info(f"GET /api/v1/books/price-range chamado por IP: {request.client.host if request else 'indefinido'}")
    livros = carregar_livros()
    resultado = []
    for livro in livros:
        preco_txt = livro.get("Preço", "0").replace(",", ".")
        try:
            preco = float(preco_txt) / 100
            if min <= preco <= max:
                resultado.append(livro)
        except:
            continue
    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Nenhum livro encontrado nesta faixa de preço."
        )
    return resultado

@app.get(
    "/api/v1/ml/features",
    summary="Dados formatados para features de ML",
    description=(
        "Retorna uma lista de dicionários contendo apenas os campos relevantes para uso como features em modelos de Machine Learning. "
    )
)
def ml_features(request: Request):
    """
    Prepara os dados do catálogo de livros para uso direto em modelos de ML.
    Mantém apenas os principais atributos (título, categoria, preço, rating, disponibilidade).
    """
    logger.info(f"GET /api/v1/ml/features chamado por IP: {request.client.host}")
    livros = carregar_livros()
    print(livros[0].keys())
    features = []
    for livro in livros:
        features.append({
            "titulo": livro.get("Título"),
            "categoria": livro.get("Categoria"),
            "preco": float(livro.get("Preço", 0)),
            "rating": livro.get("Rating"),
            "disponibilidade": livro.get("Disponibilidade")
        })
    return features

@app.get(
    "/api/v1/ml/training-data",
    summary="Dataset para treinamento de ML",
    description=(
        "Retorna o dataset completo de livros extraído do arquivo CSV original. "
    )
)
def ml_training_data(request: Request):
    """
    Endpoint para acessar o conjunto de dados bruto, pronto para treino/teste em projetos de Machine Learning.
    Não realiza limpeza ou engenharia de features; é útil como base para extração manual ou automática.
    """
    logger.info(f"GET /api/v1/ml/training-data chamado por IP: {request.client.host}")
    livros = carregar_livros()
    return livros

@app.post(
    "/api/v1/ml/predictions",
    summary="Recebe features e retorna predição",
    description=(
        "Recebe os dados de um livro via JSON e retorna uma predição com base nesses dados. "
    )
)
def ml_predictions(features: LivroFeatures, request: Request):
    """
    Endpoint POST para previsão de classificação, recomendação ou categoria de um livro a partir de suas features. 
    No exemplo, se o preço for maior que 50, retorna 'luxo'; caso contrário, 'popular'.
    Este endpoint serve como esqueleto para integração de modelos ML reais.
    """
    logger.info(f"POST /api/v1/ml/predictions chamado por IP: {request.client.host}")
    if features.preco > 50:
        pred = "luxo"
    else:
        pred = "popular"
    return {
        "inputs": features.dict(),
        "predicted_label": pred,
    }
