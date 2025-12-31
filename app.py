import streamlit as st
import pandas as pd
import psycopg2
from datetime import date

# ================= CONFIG =======================
st.set_page_config(page_title="Controle Financeiro", page_icon="💸", layout="wide")
st.title("💸 Controle Financeiro")

# ================= BANCO DE DADOS =================

# Pega do secrets da hospedagem (Streamlit Cloud)
DATABASE_URL = st.secrets.get("DATABASE_URL")

if not DATABASE_URL:
    st.error("❌ DATABASE_URL não encontrado! Confira os Secrets no Streamlit Cloud.")
    st.stop()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lancamentos (
        id SERIAL PRIMARY KEY,
        data DATE NOT NULL,
        tipo TEXT NOT NULL,
        referente TEXT NOT NULL,
        valor NUMERIC(10,2) NOT NULL,
        mes TEXT NOT NULL
    )
    """)
    conn.commit()

except Exception as e:
    st.error(f"❌ Erro ao conectar no banco: {e}")
    st.stop()


# ================= FUNÇÕES =======================
def salvar_lancamento(data, tipo, referente, valor, mes):
    cursor.execute(
        "INSERT INTO lancamentos (data, tipo, referente, valor, mes) VALUES (%s, %s, %s, %s, %s)",
        (data, tipo, referente, valor, mes)
    )
    conn.commit()


def listar_lancamentos():
    cursor.execute("SELECT * FROM lancamentos ORDER BY data DESC, id DESC")
    registros = cursor.fetchall()
    colunas = ["ID", "Data", "Tipo", "Referente", "Valor", "Mês"]
    return pd.DataFrame(registros, columns=colunas)


# ================= INTERFACE ======================

st.subheader("📌 Novo Lançamento")

col1, col2, col3 = st.columns(3)
data = col1.date_input("Data", value=date.today())
tipo = col2.selectbox("Tipo", ["Entrada", "Saída"])
referente = col3.text_input("Referente")

col4, col5 = st.columns(2)
valor = col4.number_input("Valor (R$)", min_value=0.0, format="%.2f")
mes = col5.selectbox("Mês", 
    ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
     "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
)

if st.button("💾 Salvar Lançamento"):
    if referente and valor > 0:
        salvar_lancamento(data, tipo, referente, valor, mes)
        st.success("✔️ Lançamento registrado!")
    else:
        st.warning("⚠️ Preencha todos os campos!")

st.divider()

# ================= LISTAGEM =======================
st.subheader("📋 Lançamentos Registrados")

df = listar_lancamentos()
st.dataframe(df, use_container_width=True)

# ================= TOTALIZAÇÃO ====================
if not df.empty:
    total_entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
    total_saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()
    saldo = total_entradas - total_saidas

    st.metric("Total Entradas 💰", f"R$ {total_entradas:.2f}")
    st.metric("Total Saídas 🧾", f"R$ {total_saidas:.2f}")
    st.metric("Saldo Final 🏦", f"R$ {saldo:.2f}")
else:
    st.info("Nenhum lançamento registrado ainda.")

