import json
import requests
import streamlit as st
import pandas as pd
from pathlib import Path

# ==== CONFIGURAÇÃO ====
OLLAMA_URL = "http://localhost:11434/api/chat"

# 🔥 ULTRA LEVE (AGORA FUNCIONA NO SEU PC)
MODELO = "tinyllama"

DATA_DIR = Path("./data")

# ==== VERIFICAR OLLAMA ====
def iniciar_ollama():
    try:
        r = requests.get("http://localhost:11434", timeout=2)
        return r.status_code == 200
    except:
        return False

# ==== CARREGAR DADOS ====
@st.cache_data
def carregar_dados():
    try:
        with open(DATA_DIR / 'perfil_investidor.json', encoding='utf-8') as f:
            perfil = json.load(f)

        with open(DATA_DIR / 'produtos_financeiros.json', encoding='utf-8') as f:
            produtos = json.load(f)

        transacoes = pd.read_csv(DATA_DIR / 'transacoes.csv')
        historico = pd.read_csv(DATA_DIR / 'historico_atendimento.csv')

        return perfil, produtos, transacoes, historico

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

# ==== SYSTEM PROMPT ====
SYSTEM_PROMPT = """Você é o Credix, um educador financeiro simples e didático.

Explique tudo de forma MUITO simples e curta.
Não recomende investimentos.
Use exemplos básicos.
No máximo 2 parágrafos.
Sempre pergunte se entendeu.
"""

# ==== CONTEXTO (ENXUGADO PRA FICAR MAIS LEVE) ====
def montar_contexto(perfil, produtos, transacoes, historico):
    return f"""
Cliente: {perfil['nome']}
Idade: {perfil['idade']}
Perfil: {perfil['perfil_investidor']}
Objetivo: {perfil['objetivo_principal']}
Patrimônio: R$ {perfil['patrimonio_total']}

Últimas transações:
{transacoes.tail(3).to_string(index=False)}
"""

# ==== CHAMAR OLLAMA ====
def perguntar(pergunta, contexto):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{contexto}\n\nPergunta: {pergunta}"}
                ],
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return f"Erro HTTP: {response.status_code}"

        data = response.json()
        return data["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        return "Erro: Ollama não está rodando."
    except requests.exceptions.Timeout:
        return "Erro: demora na resposta."
    except Exception as e:
        return f"Erro: {e}"

# ==== INTERFACE ====
st.set_page_config(page_title="Credix", layout="centered")
st.title("💰 Credix - Educador Financeiro")

if not iniciar_ollama():
    st.error("Ollama não está rodando. Execute: ollama serve")
    st.stop()

perfil, produtos, transacoes, historico = carregar_dados()
contexto = montar_contexto(perfil, produtos, transacoes, historico)

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    st.chat_message(msg["role"]).write(msg["content"])

pergunta_user = st.chat_input("Pergunte sobre finanças...")

if pergunta_user:
    st.session_state.chat.append({"role": "user", "content": pergunta_user})
    st.chat_message("user").write(pergunta_user)

    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta_user, contexto)

    st.session_state.chat.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
