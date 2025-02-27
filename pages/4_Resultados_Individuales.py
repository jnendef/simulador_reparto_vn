### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64
# import logging

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

from datetime import datetime

from pages.pages_content.page4 import obtencion_datos_usr, datos_matriz, preparacion_lista, obtencion_indices, grafico_prod_total
from pages.pages_content.page4 import dataframes_datos, graficado_energia, graficado_coef, coeficientes_intervalo

tipologiaSB = {
    6:"Apartamento un adulto calefacción eléctrica",
    7:"Apartamento un adulto calefacción gas",
    9:"Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8:"Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"Piso dos adultos, calefacción gas y AC",
    10:"Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

st.markdown("# Resultados")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))

try:
    st.markdown("## Comunidad: "+str(st.session_state.nComunidad))
    st.markdown("## Simulación para el Año: "+str(st.session_state.anyo))

    datosUsr = obtencion_datos_usr()

    redListaU, diccioUsr, mDatos = datos_matriz(datosUsr)

    # mConsumos = [mDatos[i,:,0].sum(0) for i in range(len(datosUsr))]
    # mCoef = [mDatos[i,:,1].mean(0) for i in range(len(datosUsr))]
    # mReparto = [mDatos[i,:,2].sum(0) for i in range(len(datosUsr))]
    # mExcedentes = [mDatos[i,:,3].sum(0) for i in range(len(datosUsr))]
    eleccion = preparacion_lista(redListaU)

    start_time = st.date_input("fecha inicio",value=datetime(st.session_state.anyo, 1, 1, 0, 0))

    end_time = st.date_input("fecha fin", value=datetime(st.session_state.anyo+1, 1, 1, 0, 0))

    df0, df1, df2, df3, df4 = dataframes_datos(start_time, end_time, eleccion, diccioUsr, mDatos)
    
    indices = obtencion_indices(start_time, end_time)

    st.markdown("### Gráfica de Producción total Comunidad")
    grafico_prod_total(mDatos,start_time,end_time,indices)
    
    st.markdown("### Gráfica de Consumo, Reparto y Excedentes")
    graficado_energia(df0, df2, df3, df4, indices)
    
    st.markdown("### Coeficientes de reparto")
    graficado_coef(df1,indices)

    st.markdown("## Coeficientes del intervalo")
    cups = st.text_input("CUPS", value="", max_chars=22)
    if cups != "" and len(cups)==22:
        coeficientes_intervalo(start_time, end_time,indices,df1, cups)

    col1,col2,col3 = st.columns(3)

    with col3:
        st.markdown(
            """<a href="https://endef.com/">
            <img src="data:;base64,{}" width="200">
            </a>""".format(
                base64.b64encode(open("path1.png", "rb").read()).decode()
            ),
            unsafe_allow_html=True,
        )
except:
    pass