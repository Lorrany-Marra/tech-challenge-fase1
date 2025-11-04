import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard API Livros", layout="wide")

# Logo FIAP
img_path = os.path.join(os.path.dirname(__file__), 'logo-fiap.png')
if os.path.exists(img_path):
    try:
        st.sidebar.image(img_path, use_container_width=True, caption="FIAP - Tech Challenge")
    except Exception:
        st.sidebar.write("**FIAP - Tech Challenge**")
else:
    st.sidebar.write("**FIAP - Tech Challenge**")

# Caminho do arquivo de logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs_api.json')

# Carregamento de logs
logs = []
if os.path.exists(log_path):
    try:
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    j = json.loads(line)
                    if "endpoint" in j and "response_time_ms" in j:
                        logs.append(j)
                except Exception:
                    pass
    except Exception as e:
        st.error(f"Erro ao carregar logs: {e}")

# Para execução se não houver logs
if not logs:
    st.warning("Nenhum log disponível. Faça algumas requisições à API primeiro!")
    st.stop()

# Cria DataFrame
df = pd.DataFrame(logs)

# Remove endpoint raiz
if 'endpoint' in df.columns:
    df = df[df['endpoint'] != '/']

# Para se ficou vazio após filtro
if len(df) == 0:
    st.warning("Nenhum log válido. Aguardando requisições...")
    st.stop()

# === INTERFACE ===
st.title("Dashboard de Uso e Monitoramento - Books API")
st.markdown("---")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Requisições", len(df))

avg_time = round(df['response_time_ms'].mean(), 2) if 'response_time_ms' in df.columns and len(df) > 0 else 0
col2.metric("Tempo Médio (ms)", avg_time)

if 'status_code' in df.columns and len(df) > 0:
    error_rate = round(100 * (df['status_code'] >= 400).sum() / len(df), 2)
else:
    error_rate = 0
col3.metric("Taxa de Erro (%)", error_rate)

unique_endpoints = df["endpoint"].nunique() if 'endpoint' in df.columns and len(df) > 0 else 0
col4.metric("Endpoints Únicos", unique_endpoints)

# Gráficos
if 'endpoint' in df.columns and len(df) > 0:
    st.markdown("### Endpoints mais acessados")
    st.bar_chart(df["endpoint"].value_counts())

if 'status_code' in df.columns and len(df) > 0:
    st.markdown("### Distribuição dos Status HTTP (por código)")
    st.bar_chart(df["status_code"].value_counts())

if 'endpoint' in df.columns and 'response_time_ms' in df.columns and len(df) > 0:
    st.markdown("### Tempo médio de resposta por endpoint")
    st.bar_chart(df.groupby("endpoint")["response_time_ms"].mean())

if 'response_time_ms' in df.columns and len(df) > 0:
    st.markdown("### Linha do tempo dos tempos de resposta das requisições")
    st.line_chart(df["response_time_ms"])

# Tabela
if len(df) > 0:
    st.markdown("### Últimas 10 requisições")
    colunas_exibir = [c for c in df.columns if c != "message"]
    st.dataframe(df[colunas_exibir].tail(10), use_container_width=True, hide_index=True)
