
import os
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# =========================================
# CONFIGURACAO
# =========================================

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
MODELO = "openai/gpt-oss-120b"

st.set_page_config(
    page_title="Meu Chat IA",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# PERSONALIDADES
# =========================================

PERSONALIDADES = {
    "Equilibrada": (
        "Você é um assistente útil, educado e claro. "
        "Responda de forma natural e objetiva."
    ),
    "Professora": (
        "Você é uma professora paciente e didática. "
        "Explique passo a passo e use exemplos simples."
    ),
    "Criativa": (
        "Você é uma assistente criativa. Ajude com ideias, "
        "textos, projetos e soluções originais."
    ),
    "Profissional": (
        "Você é um assistente profissional. "
        "Responda com clareza, precisão e organização."
    ),
    "Engraçada": (
        "Você é uma assistente bem-humorada. "
        "Use um tom leve e divertido, mantendo a utilidade."
    ),
}

FUNDOS = {
    "Grafite": "#101014",
    "Preto": "#08080C",
    "Roxo noturno": "#171024",
    "Azul noturno": "#0B1424",
    "Verde escuro": "#0B1A16",
    "Rosa escuro": "#24101D",
    "Cinza": "#202024",
    "Claro": "#F4F2F8",
}

# =========================================
# ESTADO DA SESSAO
# =========================================

if "conversas" not in st.session_state:
    primeiro_id = str(uuid.uuid4())
    st.session_state.conversas = [{
        "id": primeiro_id,
        "titulo": "Novo chat",
        "mensagens": [],
        "criada_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    }]
    st.session_state.chat_ativo = primeiro_id

if "personalidade" not in st.session_state:
    st.session_state.personalidade = "Equilibrada"

if "fundo" not in st.session_state:
    st.session_state.fundo = "#101014"

if "mensagem_pendente" not in st.session_state:
    st.session_state.mensagem_pendente = None

# Acessar conversa ativa
def obter_chat_ativo():
    for chat in st.session_state.conversas:
        if chat["id"] == st.session_state.chat_ativo:
            return chat

    # Recuperar o estado caso a conversa tenha sido removida
    chat = {
        "id": str(uuid.uuid4()),
        "titulo": "Novo chat",
        "mensagens": [],
        "criada_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    st.session_state.conversas.insert(0, chat)
    st.session_state.chat_ativo = chat["id"]
    return chat


def novo_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.conversas.insert(0, {
        "id": chat_id,
        "titulo": "Novo chat",
        "mensagens": [],
        "criada_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    st.session_state.chat_ativo = chat_id
    st.session_state.mensagem_pendente = None


def abrir_chat(chat_id):
    st.session_state.chat_ativo = chat_id
    st.session_state.mensagem_pendente = None


def excluir_chat(chat_id):
    st.session_state.conversas = [
        chat for chat in st.session_state.conversas
        if chat["id"] != chat_id
    ]

    if st.session_state.chat_ativo == chat_id:
        st.session_state.chat_ativo = (
            st.session_state.conversas[0]["id"]
            if st.session_state.conversas
            else None
        )


# =========================================
# CARREGAR IDENTIDADE VISUAL
# =========================================

arquivo_css = BASE_DIR / "style.css"

if arquivo_css.exists():
    css = arquivo_css.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )

cor_fundo = st.session_state.fundo

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {cor_fundo} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# BARRA LATERAL
# =========================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-symbol">✦</div>
            <div>
                <div class="brand-name">Meu Chat IA</div>
                <div class="brand-caption">Seu espaço inteligente</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Criar uma nova conversa
    if st.button(
        "＋  Novo chat",
        key="criar_novo_chat",
        use_container_width=True,
        type="primary"
    ):
        novo_chat()
        st.rerun()

    st.markdown("### Histórico")

    st.caption(
        f"{len(st.session_state.conversas)} conversas"
    )

    # Mostrar conversas da mais recente para a mais antiga
    for chat in list(st.session_state.conversas):
        chat_id = chat["id"]
        ativo = chat_id == st.session_state.chat_ativo

        titulo = chat["titulo"]
        if len(titulo) > 25:
            titulo = titulo[:22] + "..."

        col_abrir, col_excluir = st.columns([5, 1])

        with col_abrir:
            prefixo = "● " if ativo else "○ "

            if st.button(
                prefixo + titulo,
                key=f"abrir_{chat_id}",
                use_container_width=True,
                type="secondary" if not ativo else "primary"
            ):
                abrir_chat(chat_id)
                st.rerun()

        with col_excluir:
            if st.button(
                "×",
                key=f"excluir_{chat_id}",
                help="Excluir esta conversa"
            ):
                excluir_chat(chat_id)
                st.rerun()

    st.divider()

    # Personalidade
    st.markdown("### Personalidade da IA")

    personalidade = st.selectbox(
        "Estilo de resposta",
        list(PERSONALIDADES.keys()),
        key="seletor_personalidade",
        index=list(PERSONALIDADES.keys()).index(
            st.session_state.personalidade
        )
    )
    st.session_state.personalidade = personalidade

    st.divider()

    # Fundo personalizável
    st.markdown("### Aparência")

    nomes_fundos = list(FUNDOS.keys())
    nome_fundo_atual = next(
        (
            nome for nome, cor in FUNDOS.items()
            if cor == st.session_state.fundo
        ),
        "Personalizado"
    )

    opcoes_fundos = nomes_fundos + ["Personalizado"]

    tema = st.selectbox(
        "Tema de fundo",
        opcoes_fundos,
        index=opcoes_fundos.index(nome_fundo_atual),
        key="seletor_tema"
    )

    if tema != "Personalizado":
        st.session_state.fundo = FUNDOS[tema]

    cor_personalizada = st.color_picker(
        "Escolher uma cor",
        value=st.session_state.fundo,
        key="cor_fundo_picker"
    )
    st.session_state.fundo = cor_personalizada

    st.caption("As conversas ficam disponíveis durante esta sessão.")

# =========================================
# CONVERSA ATIVA
# =========================================

chat = obter_chat_ativo()

# =========================================
# CABECALHO PRINCIPAL
# =========================================

col_titulo, col_novo = st.columns([5, 1.5])

with col_titulo:
    st.markdown(
        """
        <div class="main-brand">
            <span class="main-symbol">✦</span>
            <span>Meu Chat IA</span>
        </div>
        <div class="main-subtitle">
            Suas ideias começam aqui.
        </div>
        """,
        unsafe_allow_html=True
    )

with col_novo:
    st.write("")
    if st.button(
        "＋ Novo chat",
        key="novo_chat_topo",
        use_container_width=True
    ):
        novo_chat()
        st.rerun()

st.divider()

# =========================================
# TELA INICIAL OU HISTORICO
# =========================================

if not chat["mensagens"]:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-symbol">✧</div>
            <h2>Como posso ajudar você?</h2>
            <p>
                Pergunte, explore ideias, aprenda algo novo
                ou comece um projeto.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### Sugestões para começar")

    col1, col2 = st.columns(2)

    sugestoes = [
        ("📚  Estudos", "Me ajude a organizar meus estudos."),
        ("💻  Programação", "Explique Python para iniciantes."),
        ("✍️  Escrita", "Ajude-me a escrever um texto."),
        ("💡  Criatividade", "Dê ideias para um projeto criativo."),
    ]

    for i, (rotulo, mensagem) in enumerate(sugestoes):
        coluna = col1 if i % 2 == 0 else col2

        with coluna:
            if st.button(
                rotulo,
                key=f"sugestao_{chat['id']}_{i}",
                use_container_width=True
            ):
                st.session_state.mensagem_pendente = mensagem
                st.rerun()

else:
    st.markdown(
        f'<div class="chat-title">{chat["titulo"]}</div>',
        unsafe_allow_html=True
    )

# Mostrar mensagens da conversa selecionada
for mensagem in chat["mensagens"]:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

# =========================================
# CAMPO DE MENSAGEM
# =========================================

mensagem_digitada = st.chat_input(
    "Escreva sua mensagem..."
)

if st.session_state.mensagem_pendente:
    pergunta = st.session_state.mensagem_pendente
    st.session_state.mensagem_pendente = None
else:
    pergunta = mensagem_digitada

# =========================================
# RESPOSTA DA GROQ
# =========================================

if pergunta:
    if not API_KEY:
        st.error(
            "Chave da API não encontrada. "
            "Configure GROQ_API_KEY no arquivo .env."
        )
        st.stop()

    # Guardar a mensagem na conversa atual
    chat["mensagens"].append({
        "role": "user",
        "content": pergunta
    })

    # Criar título a partir da primeira mensagem
    if chat["titulo"] == "Novo chat":
        chat["titulo"] = " ".join(pergunta.split())[:32]
        if len(pergunta.strip()) > 32:
            chat["titulo"] += "..."

    with st.chat_message("user"):
        st.markdown(pergunta)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                client = Groq(api_key=API_KEY)

                mensagens_api = [{
                    "role": "system",
                    "content": PERSONALIDADES[personalidade]
                }]

                mensagens_api.extend(chat["mensagens"])

                resposta = client.chat.completions.create(
                    model=MODELO,
                    messages=mensagens_api
                )

                texto = resposta.choices[0].message.content

                if not texto:
                    texto = "Não consegui gerar uma resposta."

            st.markdown(texto)

        chat["mensagens"].append({
            "role": "assistant",
            "content": texto
        })

    except Exception as erro:
        # Retirar a pergunta que não recebeu resposta
        if (
            chat["mensagens"]
            and chat["mensagens"][-1]["role"] == "user"
        ):
            chat["mensagens"].pop()

        st.error("Não foi possível obter uma resposta da IA.")

        with st.expander("Detalhes do erro"):
            st.code(str(erro))

        st.caption(
            "Confira a chave da API, a conexão e o modelo escolhido."
        )
