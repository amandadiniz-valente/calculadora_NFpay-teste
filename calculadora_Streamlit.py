# calculadora_streamlit.py
import streamlit as st
import unicodedata

DEBUG = False

def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s

def escolher_taxa_antecipacao(tipo_pessoa_raw: str):
    t = normalize_text(tipo_pessoa_raw)
    if t in ("f", "fisica", "pessoa fisica", "pf"):
        return 0.069
    if t in ("j", "juridica", "pessoa juridica", "pj"):
        return 0.038
    raise ValueError("Tipo de pessoa inválido.")

def calcular_valor_liquido(venda: float, antecipado: bool, tipo_pessoa_raw: str = None, parcelas: int = 1):
    taxa_maquininha = 0.0249
    if not antecipado:
        valor_liquido = venda * (1 - taxa_maquininha)
        desconto_maquininha = venda - valor_liquido
        return [{
            "parcela": 1,
            "valor_parcela": venda,
            "valor_com_taxa_maquininha": valor_liquido,
            "desconto_maquininha": desconto_maquininha,
            "desconto_antecipacao_val": 0.0,
            "valor_antecipado": valor_liquido,
            "meses_antecipados": 0
        }]
    taxa_antecipacao = escolher_taxa_antecipacao(tipo_pessoa_raw)
    resultados = []
    valor_parcela = venda / parcelas
    for i in range(1, parcelas + 1):
        mes_antecipado = i
        valor_com_taxa = valor_parcela * (1 - taxa_maquininha)
        desconto_maquininha = valor_parcela - valor_com_taxa
        desconto_antecipacao_percent = taxa_antecipacao * mes_antecipado
        if desconto_antecipacao_percent > 1:
            desconto_antecipacao_percent = 1.0
        desconto_antecipacao_val = valor_com_taxa * desconto_antecipacao_percent
        valor_antecipado = valor_com_taxa - desconto_antecipacao_val
        resultados.append({
            "parcela": i,
            "valor_parcela": valor_parcela,
            "valor_com_taxa_maquininha": valor_com_taxa,
            "desconto_maquininha": desconto_maquininha,
            "desconto_antecipacao_val": desconto_antecipacao_val,
            "desconto_antecipacao_percent": desconto_antecipacao_percent,
            "valor_antecipado": valor_antecipado,
            "meses_antecipados": mes_antecipado
        })
    return resultados

# ---- Interface Streamlit ----
st.title("📊 Calculadora de Taxas - Maquininha & Antecipação")

venda = st.number_input("Digite o valor da venda (R$):", min_value=0.0, step=0.01, format="%.2f")
antecipado = st.radio("O valor será antecipado?", ["Não", "Sim"]) == "Sim"

if antecipado:
    tipo_pessoa = st.radio("Cliente é Pessoa Física ou Jurídica?", ["Física", "Jurídica"])
    parcelas = st.number_input("Número de parcelas:", min_value=1, step=1, value=1)
else:
    tipo_pessoa = None
    parcelas = 1

if st.button("Calcular"):
    resultados = calcular_valor_liquido(venda, antecipado, tipo_pessoa, parcelas)
    total_liquido = sum(r["valor_antecipado"] for r in resultados)

    st.subheader("💰 Resultado do Cálculo")
    st.write(f"**Total líquido a receber:** R$ {total_liquido:.2f}")

    st.table([{
        "Parcela": r["parcela"],
        "Valor Bruto": f"R$ {r['valor_parcela']:.2f}",
        "Após Taxa Maquininha": f"R$ {r['valor_com_taxa_maquininha']:.2f}",
        "Desconto Maquininha": f"R$ {r['desconto_maquininha']:.2f}",
        "Taxa Antecipação (%)": f"{r.get('desconto_antecipacao_percent', 0)*100:.2f}%",
        "Desconto Antecipação": f"R$ {r['desconto_antecipacao_val']:.2f}",
        "Valor Líquido Parcela": f"R$ {r['valor_antecipado']:.2f}"
    } for r in resultados])
