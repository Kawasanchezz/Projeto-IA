import json
import requests # type: ignore
import streamlit as st # type: ignore
import pandas as pd # type: ignore
from pathlib import Path

# ==== CONFIGURAÇÃO ====
OLLAMA_URL = "http://localhost:11434/api/chat"

# 🔥 MODELO LEVE (IMPORTANTE)
MODELO = "phi3"

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
SYSTEM_PROMPT = """Você é o Credix, um educador financeiro amigável e didático.

OBJETIVO:
Ensinar finanças pessoais de forma simples usando exemplos do cliente.

REGRAS:
- Nunca recomende investimentos específicos
- Não responda fora do tema finanças pessoais
- Use linguagem simples
- Use os dados do cliente como exemplo
- Seja direto (máximo 3 parágrafos)
- Sempre pergunte se o cliente entendeu
"""

# ==== CONTEXTO ====
def montar_contexto(perfil, produtos, transacoes, historico):
    return f"""
Cliente: {perfil['nome']} ({perfil['idade']} anos)
Perfil: {perfil['perfil_investidor']}
Objetivo: {perfil['objetivo_principal']}
Patrimônio: R$ {perfil['patrimonio_total']}
Reserva: R$ {perfil['reserva_emergencia_atual']}

Transações recentes:
{transacoes.tail(5).to_string(index=False)}

Histórico:
{historico.tail(5).to_string(index=False)}
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
            return f"Erro HTTP: {response.status_code} - {response.text}"

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

# verificar ollama
if not iniciar_ollama():
    st.error("Ollama não está rodando. Execute: ollama serve")
    st.stop()

# carregar dados
perfil, produtos, transacoes, historico = carregar_dados()
contexto = montar_contexto(perfil, produtos, transacoes, historico)

# memória do chat
if "chat" not in st.session_state:
    st.session_state.chat = []

# mostrar histórico
for msg in st.session_state.chat:
    st.chat_message(msg["role"]).write(msg["content"])

# input
pergunta_user = st.chat_input("Pergunte sobre finanças...")

if pergunta_user:
    st.session_state.chat.append({"role": "user", "content": pergunta_user})
    st.chat_message("user").write(pergunta_user)

    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta_user, contexto)

    st.session_state.chat.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
