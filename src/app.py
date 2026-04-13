import json
import subprocess
import time
import requests
import streamlit as st
import pandas as pd
from pathlib import Path

#==== CONFIGURAÇÃO ====
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO     = "llama3"
DATA_DIR   = Path("./data")

#==== INICIAR OLLAMA AUTOMATICAMENTE ====
def iniciar_ollama():
    try:
        r = requests.get("http://localhost:11434", timeout=3)
        if r.status_code == 200:
            return True
    except requests.exceptions.ConnectionError:
        pass

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW  # sem janela no Windows
        )
        time.sleep(3)
        return True
    except FileNotFoundError:
        return False

#===== CARREGAR DADOS ======
@st.cache_data
def carregar_dados():
    try:
        with open(DATA_DIR / 'perfil_investidor.json', encoding='utf-8') as f:
            perfil = json.load(f)
        with open(DATA_DIR / 'produtos_financeiros.json', encoding='utf-8') as f:
            produtos = json.load(f)

        transacoes = pd.read_csv(DATA_DIR / 'transacoes.csv')
        historico  = pd.read_csv(DATA_DIR / 'historico_atendimento.csv')
        return perfil, produtos, transacoes, historico

    except FileNotFoundError as e:
        st.error(f"Arquivo não encontrado: {e}")
        st.stop()
    except (json.JSONDecodeError, pd.errors.ParserError) as e:
        st.error(f"Erro ao ler arquivo: {e}")
        st.stop()

#==== SYSTEM PROMPT ====
SYSTEM_PROMPT = """Você é o Credix, um educador financeiro amigavel e didático.

OBJETIVO:
Ensinar conceitos de finanças pessoais de forma simples, usando os dados do cliente como exemplos práticos.

REGRAS:
-NUNCA recomende investimentos específicos, apenas explique como funcionam;
-JAMAIS responder a pergunta fora do tema ensino de finança pessoais,
Quando ocorrer, responda lembrano o seu papel de educador financeiro;
-Use os dados fornecidos para dar exemplos personalizados;
-Linguagem simples, como explicasse para um amigo;
-Se não souber algo, admita: "Não tenho essa informação, mas posso explicar...";
-Sempre perguntar se o cliente entendeu;
-Responda de forma sucinta e direta, com maximo 3 parágrafos;
"""

#==== MONTAR CONTEXTO ====
def montar_contexto(perfil, produtos, transacoes, historico):
    return f"""
Clientes: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

#==== CHAMAR OLLAMA ====
def perguntar(msg: str, contexto: str) -> str:
    if not msg or not msg.strip():
        return "Por favor, digite uma pergunta."

    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{contexto}\n\nPergunta: {msg.strip()}"}
    ]

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "messages": mensagens,
                "stream": False
            },
            timeout=60
        )
        r.raise_for_status()

        resposta = r.json().get("message", {}).get("content", "").strip()

        return resposta if resposta else "Não obtive resposta do modelo."

    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar ao Ollama."
    except requests.exceptions.Timeout:
        return "Erro: o modelo demorou demais para responder."
    except requests.exceptions.HTTPError as e:
        return f"Erro HTTP: {e}"
    except (KeyError, ValueError):
        return "Erro: resposta inesperada do modelo."

#=== INTERFACE ===
st.title("| Credix, seu educador Financeiro")

# Inicia Ollama se não estiver rodando
if not iniciar_ollama():
    st.error("Ollama não encontrado. Instale em: https://ollama.com/download")
    st.stop()

# Carrega dados
perfil, produtos, transacoes, historico = carregar_dados()
contexto = montar_contexto(perfil, produtos, transacoes, historico)

# Histórico do chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).write(msg["content"])

# Nova pergunta
if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    st.chat_message("user").write(pergunta)

    with st.spinner("Pensando..."):
        resposta = perguntar(pergunta, contexto)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)
