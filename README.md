# API de Livros - Tech Challenge Fase 1

> **Pós-Graduação em Machine Learning Engineering**
> **(FIAP)**

Sistema de extração, processamento e recomendação de livros utilizando **Web Scraping**, **API RESTful**, **Autenticação JWT** e **Dashboard de Monitoramento**.

---

## Objetivo do Projeto

Desenvolver uma solução escalável e automatizada para:

 - **Extrair dados** de livros do site: https://books.toscrape.com/
 - **Armazenar** informações em formato estruturado (CSV)  
 - **Disponibilizar** os dados via **API RESTful**  
 - **Autenticar** usuários com **JWT (JSON Web Tokens)**  
 - **Monitorar** uso e desempenho com **Dashboard Streamlit**  
 - **Preparar** dados para **Machine Learning**

---

## Tecnologias Utilizadas

### **Backend & API**
- **Python 3.12+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic** - Validação de dados e schemas
- **python-jose** - Geração e validação de tokens JWT
- **python-multipart** - Suporte a formulários multipart

### **Web Scraping**
- **BeautifulSoup4** - Extração de dados HTML
- **Requests** - Cliente HTTP

### **Processamento de Dados**
- **Pandas** - Manipulação e análise de dados
- **CSV** - Armazenamento estruturado
- **Unidecode** - Normalização de texto

### **Monitoramento & Logs**
- **Streamlit** - Dashboard interativo
- **python-json-logger** - Logs estruturados em JSON

### **Deploy & Infraestrutura**
- **Render** - API em produção
- **GitHub** - Controle de versão

---

## Arquitetura do Sistema

<img width="866" height="1024" alt="diagrama" src="https://github.com/user-attachments/assets/919e077f-5d12-48e6-b246-b0a28bdeb200" />


**Fluxo de Dados:**

1. **Web Scraping** extrai dados de livros do site `books.toscrape.com`
2. Dados são salvos em `data/livros_completo.csv`
3. **API FastAPI** lê o CSV e disponibiliza endpoints REST
4. **Autenticação JWT** protege rotas sensíveis
5. **Dashboard Streamlit** monitora métricas em tempo real
6. **Logs JSON** rastreiam todas as requisições

---

## Funcionalidades

### **Autenticação & Segurança**
- Login com usuário e senha
- Geração de tokens JWT
- Renovação de tokens (refresh)
- Proteção de rotas sensíveis

###  **Gestão de Livros**
- Listar todos os livros
- Buscar livro por ID
- Buscar por título e categoria
- Filtrar por faixa de preço
- Listar livros mais bem avaliados
- Listar categorias disponíveis

### **Estatísticas & Analytics**
- Estatísticas gerais (total, preço médio, ratings)
- Estatísticas por categoria
- Health check da API

### **Machine Learning**
- Endpoint de features para ML
- Dataset para treinamento
- Endpoint de predições (placeholder)

### **Monitoramento**
- Dashboard interativo com Streamlit
- Métricas de uso (total de requisições, tempo médio, taxa de erro)
- Gráficos de endpoints mais acessados
- Distribuição de status HTTP
- Logs estruturados em JSON

---

## Como Executar Localmente

### **1. Clone o Repositório**
git clone https://github.com/Lorrany-Marra/tech-challenge-fase1.git
cd tech-challenge-fase1


### **2. Crie e Ative Ambiente Virtual**
python -m venv venv

**Windows** -
venv\Scripts\activate

**Linux/Mac** -
source venv/bin/activate


### **3. Instale as Dependências**
pip install -r requirements.txt


### **4. Execute o Web Scraper (Opcional)**
Se quiser atualizar os dados:

python scripts/scraper_books.py


### **5. Inicie a API**
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8501


A API estará disponível em: `http://localhost:8501`

### **6. Acesse a Documentação Interativa**

Abra no navegador:
- **Swagger UI**: `http://localhost:8501/docs`
- **ReDoc**: `http://localhost:8501/redoc`

### **7. Execute o Dashboard (Terminal Separado)**
streamlit run api/dashboard.py


Dashboard disponível em: `http://localhost:8502`

---

## Endpoints da API

### ** Públicos (Sem Autenticação)**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/login` | Obtém token JWT |
| `GET` | `/api/v1/books` | Lista todos os livros |
| `GET` | `/api/v1/books/{id}` | Detalhes de um livro |
| `GET` | `/api/v1/books/search` | Busca por título/categoria |
| `GET` | `/api/v1/categories` | Lista categorias |
| `GET` | `/api/v1/health` | Status da API |
| `GET` | `/api/v1/stats/overview` | Estatísticas gerais |
| `GET` | `/api/v1/stats/categories` | Estatísticas por categoria |
| `GET` | `/api/v1/books/top-rated` | Livros melhor avaliados |
| `GET` | `/api/v1/books/price-range` | Filtra por preço |
| `GET` | `/api/v1/ml/features` | Features para ML |
| `GET` | `/api/v1/ml/training-data` | Dataset completo |
| `POST` | `/api/v1/ml/predictions` | Predições (placeholder) |

### ** Protegidos (Requerem JWT)**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/refresh` | Renova token JWT |
| `POST` | `/api/v1/scraping/trigger` | Dispara scraping (apenas admin) |

---

##  Autenticação JWT

### **1. Obter Token**

**Endpoint:** `POST /api/v1/auth/login`

**Body (form-data):**
username: admin
password: admin123


**Resposta:**
{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
"token_type": "bearer"
}


### **2. Usar Token em Requisições Protegidas**

Adicione o header:
Authorization: Bearer <coloque_o_token_aqui>


### **3. Renovar Token**

**Endpoint:** `POST /api/v1/auth/refresh` (com token válido no header)

---

## Dashboard de Monitoramento

### **Acesso**

 **Produção:** [https://desafio-tecnolgico-fase1-dpcymdwqryg6dcv9h6k6zm.streamlit.app/](https://desafio-tecnolgico-fase1-dpcymdwqryg6dcv9h6k6zm.streamlit.app/)

### **Métricas Disponíveis**

- **Total de Requisições**  
- **Tempo Médio de Resposta (ms)**  
- **Taxa de Erro (%)**  
- **Endpoints Únicos Acessados**  
- **Gráficos Interativos:**
   - Endpoints mais acessados
   - Distribuição de status HTTP
   - Tempo médio por endpoint
   - Linha do tempo de respostas
   - Últimas 10 requisições

### **Exemplo de Dashboard**
![1](https://github.com/user-attachments/assets/c8105f8f-7c49-4e61-8dae-6bbad1d9a377)
![2](https://github.com/user-attachments/assets/d2dae4f4-1292-4a20-b47b-030b997b16cf)
![3](https://github.com/user-attachments/assets/40fd62bc-16c1-41c7-86f9-ea9c6e1ed189)
![4](https://github.com/user-attachments/assets/1717b89d-bc37-4f60-9577-902d4721941f)
![5](https://github.com/user-attachments/assets/10976669-6ee8-402d-9378-f7b5e570fdae)

---

## Deploy em Produção

### **API (Render)**

 **URL:** `https://tech-challenge-fiap-api.onrender.com](https://tech-challenge-fase1-3p5d.onrender.com`

**Configuração:**
- **Runtime:** Python 3.12
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Health Check:** `/api/v1/health`

**Configuração:**
- **Main file:** `api/dashboard.py`
- **Python version:** 3.12

---

## Melhorias Futuras

### ** Banco de Dados**
- Migrar de CSV para **PostgreSQL** ou **MongoDB**
- Implementar cache com **Redis**

### ** Machine Learning**
- Sistema de recomendação baseado em **Collaborative Filtering**
- Classificação automática de categorias com **NLP**
- Análise de sentimento em reviews

### **Escalabilidade**
- Containerização com **Docker**
- Orquestração com **Kubernetes**
- CI/CD com **GitHub Actions**

### ** Monitoramento Avançado**
- Integração com **Prometheus + Grafana**
- Alertas automáticos para erros
- Análise de logs com **ELK Stack**

---

## Referências

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [JWT.io](https://jwt.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Render Deployment Guide](https://render.com/docs)
- Material didático FIAP - Fase 1

---

## Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do **Tech Challenge da FIAP**.

---

##  Vídeo de Apresentação

 **Link do vídeo:** (https://youtube.com/watch?v=wS_obu3BRGo&feature=shared)
 
**Conteúdo:**
- Demonstração da API funcionando
- Testes de endpoints no Swagger
- Visualização do Dashboard
- Explicação da arquitetura
- Demonstração do código principal

---

**Desenvolvido por Lorrany Marra**

