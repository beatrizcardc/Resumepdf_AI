import streamlit as st
import pdfplumber
import pandas as pd
import re
import requests
from io import BytesIO

# Configuração do Streamlit
st.set_page_config(layout="wide", page_title="Fine-tuning - Extração de Termos de Aditamento")

# Base URL para os PDFs no GitHub
base_url = "https://raw.githubusercontent.com/beatrizcardc/MonitoramentoROD/main/termos_aditamento"
pdf_files = [
    "termo1.pdf", 
    "termo2.pdf", 
    "termo3.pdf", 
    "termo4.pdf"
]

# Função para carregar PDFs do GitHub
def load_pdf_from_github(file_name):
    url = f"{base_url}/{file_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        st.error(f"Erro ao acessar o PDF: {file_name} (Status: {response.status_code})")
        return None

# Função para extrair texto e informações categorizadas de um PDF
def extract_info_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Definição de padrões para categorias
    info = {
        "Condição de Atualização do Crédito": extract_pattern(
            text, r"(IPCA|tabela do fabricante|INCC|INPC|FIPE)"
        ),
        "Formas de Aquisição do Bem": extract_pattern(
            text, r"(consórcio|compra direta|lance vinculado|lance livre)"
        ),
        "Contemplações e Observações": extract_pattern(
            text, r"(sorteio|lance livre|lance fixo|lance vinculado)"
        ),
        "Antecipações e Observações": extract_pattern(text, r"(antecipação|observação)"),
        "Condição de Parcela Antecipada": extract_pattern(
            text, r"(parcela antecipada|% embutido|parcelamento)"
        ),
        "Opção de Diluição do Lance": extract_pattern(text, r"(diluição do lance)"),
        "Parcela Reduzida": extract_pattern(text, r"(parcela reduzida)"),
        "Aumento de Crédito": extract_pattern(
            text, r"(aumento de crédito|assembleia do grupo)"
        ),
        "Seguro Prestamista": extract_pattern(text, r"(seguro prestamista)"),
        "Observações Adicionais": extract_pattern(text, r"(\*.*)")
    }

    return info

# Função para extrair padrões de texto
def extract_pattern(text, pattern):
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return "; ".join(set(matches)) if matches else "Não encontrado"

# Interface do Streamlit
st.title("Fine-tuning - Extração de Termos de Aditamento")
st.sidebar.header("Configurações de Entrada")

# Opção para escolher o modo de carregamento
mode = st.sidebar.radio("Escolher fonte dos PDFs", ["Subir PDFs", "Usar PDFs do GitHub"])

if mode == "Subir PDFs":
    uploaded_files = st.sidebar.file_uploader(
        "Faça upload dos PDFs dos Termos de Aditamento", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        st.sidebar.success(f"{len(uploaded_files)} arquivo(s) carregado(s).")
        process_button = st.sidebar.button("Processar PDFs")

        if process_button:
            all_data = []
            for file in uploaded_files:
                extracted_info = extract_info_from_pdf(file)
                extracted_info["Arquivo"] = file.name
                all_data.append(extracted_info)

            # Criar DataFrame com todas as informações
            df = pd.DataFrame(all_data)

            # Exibir resultados no Streamlit
            st.subheader("Resumo das Informações Extraídas")
            st.dataframe(df)

            # Opções de download
            st.subheader("Baixar Resultado")
            csv = df.to_csv(index=False)
            txt = df.to_string(index=False)

            # Botões para download
            st.download_button(
                label="Baixar em CSV",
                data=csv,
                file_name="resumo_termos_aditamento.csv",
                mime="text/csv"
            )
            st.download_button(
                label="Baixar em TXT",
                data=txt,
                file_name="resumo_termos_aditamento.txt",
                mime="text/plain"
            )

elif mode == "Usar PDFs do GitHub":
    selected_pdfs = st.sidebar.multiselect("Selecionar Termos de Aditamento", pdf_files, default=pdf_files)

    if selected_pdfs:
        process_button = st.sidebar.button("Processar Termos Selecionados")

        if process_button:
            all_data = []
            for file_name in selected_pdfs:
                pdf_data = load_pdf_from_github(file_name)
                if pdf_data:
                    extracted_info = extract_info_from_pdf(pdf_data)
                    extracted_info["Arquivo"] = file_name
                    all_data.append(extracted_info)

            # Criar DataFrame com todas as informações
            df = pd.DataFrame(all_data)

            # Exibir resultados no Streamlit
            st.subheader("Resumo das Informações Extraídas")
            st.dataframe(df)

            # Opções de download
            st.subheader("Baixar Resultado")
            csv = df.to_csv(index=False)
            txt = df.to_string(index=False)

            # Botões para download
            st.download_button(
                label="Baixar em CSV",
                data=csv,
                file_name="resumo_termos_aditamento.csv",
                mime="text/csv"
            )
            st.download_button(
                label="Baixar em TXT",
                data=txt,
                file_name="resumo_termos_aditamento.txt",
                mime="text/plain"
            )
else:
    st.sidebar.info("Escolha uma opção para processar os Termos de Aditamento.")

