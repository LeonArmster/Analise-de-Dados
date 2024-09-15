# Bibliotecas

# a pasta .streamlit com o arquivo config.toml é para configurar o tema

## biblioteca para analise de dados
import pandas as pd

## biblioteca para criação do app/dashboard
import streamlit as st

## bibliotecas para criação de mapa
import folium
from folium import plugins
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

## biblioteca para criação de gráficos
import plotly.express as px



# configurando o layout da página
st.set_page_config(page_title='Analise de Aluguéis', layout='wide')

# Configurando o título da página
st.title('Dashboard de Anáiise de Aluguéis de Imóveis nos EUA')

# Criando um separados
st.write('---')

# Carregando os dados
df = pd.read_csv('dados_tratados.csv', encoding='latin-1')

# Variáveis para controle do sidebar
dias_min = df['Dias_Anuncio'].min()
dias_max = df['Dias_Anuncio'].max()
aluguel_min = df['VL_Aluguel'].min()
aluguel_max = df['VL_Aluguel'].max()

# Variaveis para o slider de dias de anuncio
qt_min, qt_max = st.sidebar.slider('Valor Aluguel', min_value = dias_min, max_value = dias_max, value = (dias_min, dias_max))

# Variaveis para o slider de valor de anuncio
vl_min, vl_max = st.sidebar.slider('Valor Aluguel', min_value = aluguel_min, max_value = aluguel_max, value = (aluguel_min, aluguel_max))

# Variável para quantidade de quartos
qtd_quartos = st.sidebar.selectbox('Quartos', df['Quartos'].astype(int).sort_values().unique(), index = None, placeholder='Selecione...')

# Variável para quantidade de banheiros
qtd_banheiros = st.sidebar.selectbox('Banheiros', df['Banheiros'].astype(int).sort_values().unique(), index = None, placeholder='Selecione...')

# Aplicando os filtros no Dataframe para exibir as informações
if qtd_quartos == None and qtd_banheiros == None:
    df_filtro = df[(df['Dias_Anuncio'].between(qt_min, qt_max)) & df['VL_Aluguel'].between(vl_min, vl_max)]
elif qtd_quartos == None and qtd_banheiros != None:
    df_filtro = df[(df['Dias_Anuncio'].between(qt_min, qt_max)) & (df['VL_Aluguel'].between(vl_min, vl_max)) & (df['Banheiros'] == qtd_banheiros)]
elif qtd_quartos != None and qtd_banheiros == None:
    df_filtro = df[(df['Dias_Anuncio'].between(qt_min, qt_max)) & (df['VL_Aluguel'].between(vl_min, vl_max)) & (df['Quartos'] == qtd_quartos)]
else:
    df_filtro = df[(df['Dias_Anuncio'].between(qt_min, qt_max)) & (df['VL_Aluguel'].between(vl_min, vl_max)) & (df['Quartos'] == qtd_quartos) & (df['Banheiros'] == qtd_banheiros)]





# Gerando um dataframe para exibição do mapa

## Copiando os dados para uma nova variável
df_localizacao = df.copy()

## excluindos os valores nan das variáveis latitude e longitude
df_localizacao = df_localizacao.dropna(subset=['Latitude', 'Longitude'])

## juntando latitude e longitude em uma nova coluna. Importante converter os valores para str para não ter erro
df_localizacao['lat_lon'] = df_localizacao['Latitude'].astype(str) + ' - ' + df_localizacao['Longitude'].astype(str)

## Agrupando os dados por coluna para saber a quantidade por localização
df_agrup = df_localizacao.groupby(['Latitude', 'Longitude', 'lat_lon']).size().reset_index()
df_agrup.columns = ['Latitude', 'Longitude', 'Lat_Lon', 'Qtd_Imoveis']

## Separando agrupamentos com quantidade de imóveis > 10
df_agrup = df_agrup.loc[(df_agrup['Qtd_Imoveis'] > 10)]

## Criando as variáveis para criação do mapa
latitude = df_agrup['Latitude'].values
longitude = df_agrup['Longitude'].values

# Criando o mapa

## A laitude fornecida abaixo é a do EUA
mapa = folium.Map(location= [37.090240, -95.712891], zoom_start=5)

## Adicionando o módulo de fullscreen
Fullscreen().add_to(mapa)

## Criando marcadores para localidade
for lat, lon in zip(latitude, longitude):
    folium.Marker(location=[lat,lon]).add_to(mapa)

## Titulo do mapa
titulo_mapa = "Concentração de Imóveis por Região"

## Configuração em css para o título
titulo = f'<h1 style="postion:absolute;z-index:10000;left:15vw","font-size:20px"> {titulo_mapa}</h1>'
mapa.get_root().html.add_child(folium.Element(titulo))


# Gerando as informações na tela
st.write('Total de Imóveis: ', df_filtro.shape[0])


# Criando as colunas do Dashboard

# Exibindo os dados nas colunas criadas
with st.container():
    col1, col2 = st.columns(2, gap='small')

    with col1:
        st.subheader('Informações Analíticas')
        st.dataframe(df_filtro.set_index(df_filtro.columns[0]), width=720, height=420)

    with col2:
        st.subheader('Mapa Demonstrando a distribuição dos imóveis')
        st_folium(mapa, width=650, height=420)


st.empty()

with st.container():
    col3, col4 = st.columns(2, gap='small')

    with col3:
        st.subheader('Relação entre o valor do aluguem x tamanho imóvel')
        fig_tamanho = px.scatter(df_filtro, x = 'Tamanho', y = 'VL_Aluguel')
        fig_tamanho.update_layout(width=650, height=420)
        col3.plotly_chart(fig_tamanho, use_container_width=True)

    with col4:
        st.subheader('Valor dos Imóveis x Imobiliária')
        fig_valor = px.bar(df_filtro, x = 'Imobiliaria', y = 'VL_Aluguel')
        fig_valor.update_layout(width = 720, height = 420)
        col4.plotly_chart(fig_valor, use_container_width=True)