import os
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="API Livros FIAP", layout="wide")

img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo-fiap.png'))
st.sidebar.image(img_path, use_container_width=True, caption="FIAP - Tech Challenge")

log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs_api.json'))

logs = []
with open(log_path, encoding="utf-8") as f:
    for line in f:
        try:
            j = json.loads(line)
            if "endpoint" in j and "response_time_ms" in j:
                logs.append(j)
        except Exception:
            pass
df = pd.DataFrame(logs)

df = df[df['endpoint'] != '/']

st.title("Dashboard de Uso e Monitoramento - Books API")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Requisições", len(df))
col2.metric("Tempo Médio (ms)", round(df['response_time_ms'].mean(), 2))
col3.metric("Taxa de Erro (%)", round(100 * (df['status_code'] >= 400).sum() / max(len(df), 1), 2))
col4.metric("Endpoints Únicos", df["endpoint"].nunique())

st.markdown("### Endpoints mais acessados")
st.bar_chart(df["endpoint"].value_counts())

st.markdown("### Distribuição dos Status HTTP (por código)")
st.bar_chart(df["status_code"].value_counts())

st.markdown("### Tempo médio de resposta por endpoint")
st.bar_chart(df.groupby("endpoint")["response_time_ms"].mean())

st.markdown("### Linha do tempo dos tempos de resposta das requisições")
st.line_chart(df["response_time_ms"])

st.markdown("### Últimas 10 requisições")
colunas_exibir = [c for c in df.columns if c != "message"]
st.dataframe(df[colunas_exibir].tail(10), use_container_width=True, hide_index=True)

