import streamlit as st
import pandas as pd
import plotly.express as px
import gender_guesser.detector as gender
import base64

# Definindo a configuração da página como "wide"
st.set_page_config(layout="wide")

# Adicionando CSS para aumentar a largura do sidebar
st.markdown("""
    <style>
        .stSidebar.st-emotion-cache-rpj0dg.e1tphpha0 {
            width: 440px !important;
        }
        .st-emotion-cache-t1wise {
            padding: 2rem 2rem 2rem 2rem;
        }
        .st-emotion-cache-189krjl h1 {
            padding: 0rem 0rem 1rem;
        }
        .download-link {
            font-size: 14px;
            color: #1E90FF;
        }
    </style>
    """, unsafe_allow_html=True)

# Carregar a planilha
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, dtype={'CPF': str})
        df['CPF'] = df['CPF'].astype(str).str.replace(r'\D+', '', regex=True)
        # Verificar se a planilha segue o modelo esperado
        if {'NOME', 'CPF', 'EQUIPE'}.issubset(df.columns):
            return df
        else:
            st.warning("Planilha inserida não é válida. Certifique-se de que a planilha contenha as colunas NOME, CPF e EQUIPE.")
            return None
    except Exception as e:
        st.warning("Planilha inserida não é válida.")
        return None

# Função para determinar o sexo com base no primeiro nome usando a biblioteca gender-guesser
def determine_gender(name):
    if name:
        try:
            first_name = name.split()[0]
            d = gender.Detector()
            gender_result = d.get_gender(first_name)

            if gender_result == 'male':
                return 'Masculino'
            elif gender_result == 'female':
                return 'Feminino'
            else:
                if first_name.endswith(('a', 'e')):
                    return 'Feminino'
                elif first_name.endswith(('o')):
                    return 'Masculino'
                else:
                    return 'Indeterminado'
        except IndexError:
            return 'Indeterminado'
    return 'Indeterminado'

# Função para exibir gráfico de barras com plotly e centralizar o texto dentro das barras
def show_bar_chart(data):
    if 'bar_chart_loaded' not in st.session_state:
        st.session_state.bar_chart_loaded = False

    if not st.session_state.bar_chart_loaded:
        with st.spinner('Processando gráfico de número de membros por equipe'):
            team_counts = data['EQUIPE'].value_counts().reset_index()
            team_counts.columns = ['Equipe', 'Número de Membros']

            fig = px.bar(team_counts, x='Equipe', y='Número de Membros', color='Equipe',
                         color_discrete_sequence=["#00BFFF"], text='Número de Membros')

            fig.update_layout(
                title={
                    'text': "Número de Membros por Equipe",
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                height=380,
                showlegend=False
            )

            fig.update_traces(
                textposition='inside',
                texttemplate='%{text}',
                textfont_size=14,
                textfont_color='white',
                insidetextanchor='middle'
            )

            st.plotly_chart(fig, use_container_width=True)
        st.session_state.bar_chart_loaded = True
    else:
        team_counts = data['EQUIPE'].value_counts().reset_index()
        team_counts.columns = ['Equipe', 'Número de Membros']

        fig = px.bar(team_counts, x='Equipe', y='Número de Membros', color='Equipe',
                     color_discrete_sequence=["#00BFFF"], text='Número de Membros')
        
        fig.update_layout(
            title={
                'text': "Número de Membros por Equipe",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            height=380,
            showlegend=False
        )

        fig.update_traces(
            textposition='inside',
            texttemplate='%{text}',
            textfont_size=14,
            textfont_color='white',
            insidetextanchor='middle'
        )

        st.plotly_chart(fig, use_container_width=True)

# Função para exibir gráfico de pizza com a distribuição de gênero
def show_pie_chart(data):
    if 'pie_chart_loaded' not in st.session_state:
        st.session_state.pie_chart_loaded = False

    if not st.session_state.pie_chart_loaded:
        with st.spinner('Processando gráfico de distribuição de gênero'):
            data['SEXO'] = data['NOME'].apply(determine_gender)
            gender_counts = data['SEXO'].value_counts().reset_index()
            gender_counts.columns = ['Sexo', 'Número de Membros']

            fig = px.pie(gender_counts, values='Número de Membros', names='Sexo',
                         color_discrete_sequence=['#1E90FF', '#FF69B4'], hole=0.3)

            fig.update_layout(
                title={
                    'text': "Distribuição de Gênero na Equipe",
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                height=380,
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
            )

            st.plotly_chart(fig, use_container_width=True)
        st.session_state.pie_chart_loaded = True
    else:
        data['SEXO'] = data['NOME'].apply(determine_gender)
        gender_counts = data['SEXO'].value_counts().reset_index()
        gender_counts.columns = ['Sexo', 'Número de Membros']

        fig = px.pie(gender_counts, values='Número de Membros', names='Sexo',
                     color_discrete_sequence=['#1E90FF', '#FF69B4'], hole=0.3)

        fig.update_layout(
            title={
                'text': "Distribuição de Gênero na Equipe",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            height=380,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
        )

        st.plotly_chart(fig, use_container_width=True)

# Função para exibir a tabela com altura limitada
def show_data_table(data):
    st.write('**Dados Carregados:**')
    st.dataframe(data, height=300)

# Função para gerar o link de download da planilha
def download_link():
    file_path = './planilha_modelo.xlsx'  # Caminho da planilha modelo
    with open(file_path, 'rb') as f:
        file_data = f.read()
        b64 = base64.b64encode(file_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="planilha_modelo.xlsx"><button style="background-color:#4682B4; color:white; border:none; padding:5px 10px; border-radius:3px; font-size:13px;">Planilha Modelo</button></a>'
        return href

# Função principal
def main():
    st.title('Pesquisa de Equipe por CPF')

    # Exibir o botão de download da planilha logo acima do texto do sidebar
    st.sidebar.markdown(download_link(), unsafe_allow_html=True)

    file_path = st.sidebar.file_uploader('Anexar arquivo:', type=['xlsx', 'xls'])

    # Verificar se nenhum arquivo foi carregado
    if not file_path:
        st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 80vh;">
                <img src="data:image/svg+xml;base64,{}" alt="Ícone de Pasta" width="150"/>
                <p style="margin-top: 10px;"><strong>Insira um arquivo<strong></p>
            </div>
        """.format(base64.b64encode(open('icon.svg', 'rb').read()).decode()), unsafe_allow_html=True)
        return

    if file_path is not None:
        data = load_data(file_path)

        if data is not None:
            cpf_input = st.sidebar.text_input('Digite um CPF Válido:', key="cpf_input")

            if st.sidebar.button('Buscar') or cpf_input:
                if cpf_input:
                    cpf = str(cpf_input).strip()
                    cpf = cpf.replace(".", "").replace("-", "")
                    row = data[data['CPF'] == cpf]
                    if not row.empty:
                        nome = row.iloc[0]['NOME']
                        equipe = row.iloc[0]['EQUIPE']
                        
                        st.sidebar.markdown(f"""
                            <div style="background-color:#4682B4; padding: 15px; border-radius: 10px;">
                                <p style="color:white; font-size: 16px; margin: 0;"><strong>NOME:</strong> {nome}</p>
                                <p style="color:white; font-size: 16px; margin: 0;"><strong>CPF:</strong> {cpf}</p>
                                <p style="color:white; font-size: 16px; margin: 0;"><strong>EQUIPE:</strong> {equipe}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown(f"""
                            <div style="background-color:#CD5C5C; padding: 15px; border-radius: 10px;">
                                <p style="color:white; font-size: 16px; margin: 0;">CPF não encontrado</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.sidebar.markdown(f"""
                        <div style="background-color:#DAA520; padding: 15px; border-radius: 10px;">
                            <p style="color:white; font-size: 16px; margin: 0;">Por favor, insira um CPF válido</p>
                        </div>
                    """, unsafe_allow_html=True)

            show_data_table(data)

            col1, col2 = st.columns(2)
            with col1:
                show_bar_chart(data)

            with col2:
                show_pie_chart(data)

if __name__ == '__main__':
    main()
