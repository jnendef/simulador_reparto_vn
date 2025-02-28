### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql


diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                "Apartamento_1adulto_calef_gas" : 7,
                "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                "Piso_2adultos_calef_gas_aire_ac" : 12,
                "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
            }

listaDiccioTipo = list(diccioTipo)

tipologiaSB0 = [
            "Apartamento un adulto calefacción eléctrica",
            "Apartamento un adulto calefacción gas",
            "Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
            "Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
            "Piso dos adultos, calefacción gas y AC",
            "Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
        ]

tipologiaSB = {
    6:"Apartamento un adulto calefacción eléctrica",
    7:"Apartamento un adulto calefacción gas",
    9:"Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8:"Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"Piso dos adultos, calefacción gas y AC",
    10:"Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}

def obtencion_datos_usr():
    agente = Agente_MySql()
    sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
    usuarios = agente.ejecutar(sentenciaSQLusr)

    datosUsr = []

    for i in usuarios:
        sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
        datos = agente.ejecutar(sentenciaSQLdatos)
        datosUsr.append((i[10],datos))

    return datosUsr

def datos_matriz(datosUsr):
    diccioUsr = {}
    redListaU = []

    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1]),4))
    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]
        if claveUsr not in redListaU:
            redListaU.append(claveUsr)
        diccioUsr[claveUsr] = i
        for j in range(len(datosUsr[i][1])):
            for k,l in enumerate(datosUsr[i][1][j]):
                if k>2:
                    mDatos[i,j,k-3] = l

    return redListaU, diccioUsr, mDatos

def preparacion_lista(redListaU):
    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    # indicesUsr = [str(i)+" "+str(int(j.split("-")[1]))+" "+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]
    
    st.markdown("### Datos por usuario")
    eleccion0 = st.selectbox("Tipo de Usuario",[tipologiaSB[i] for i in redLista2])
    st.sidebar.write("")
    eleccion = redLista[posiRedLista[redLista2.index(diccioTipo[listaDiccioTipo[tipologiaSB0.index(eleccion0)]])]]
    
    return eleccion

def fecha(hora,dia):
    salida = dia+dt.timedelta(hours = float(hora))
    return salida

def obtencion_indices(start_time, end_time):
    fecha_ini = dt.datetime(start_time.year,start_time.month,start_time.day,0,0,0)
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horas = np.arange(start = 0,stop = (horasFin - horasInicio), step=1, dtype=int)
    indices = [fecha(i,fecha_ini) for i in horas]

    return indices

def grafico_prod_total(mDatos,start_time,end_time,indices):
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    matrizaux = mDatos[:,horasInicio:horasFin,2]
    reparto = np.sum(matrizaux,axis=0)
    
    df = pd.DataFrame(reparto,columns=["Reparto"])
    df.index = indices
    
    st.bar_chart(df, x_label="Horas", y_label= "kWh")


def dataframes_datos(start_time, end_time, eleccion, diccioUsr, mDatos):
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    df0 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,0],columns=["Consumo"])
    df1 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,1],columns=["Coeficiente"])
    df2 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,2],columns=["Reparto"])
    df3 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,3],columns=["Excedentes"])
    df4 = df2.join(-1*df3)
    df4 = df4.join((-1*df0))

    return df0, df1, df2, df3, df4

def graficado_energia(df0, df2, df3, df4, indices):
    df0.index = indices
    df2.index = indices
    df3.index = indices
    df4.index = indices

    st.bar_chart(df4, x_label="Horas", y_label= "kWh")

    st.write("Consumo Total en el intervalo kWh: {}".format(str(df0.sum()["Consumo"])[:6]))
    st.write("Reparto Total en el intervalo kWh: {}".format(str(df2.sum()["Reparto"])[:6]))
    st.write("Excedente Total en el intervalo kWh: {}".format(str(df3.sum()["Excedentes"])[:6]))

def graficado_coef(df1,indices):
    df1.index = indices
    st.line_chart(df1, x_label = "Horas", y_label = "%")
    st.write("Coeficiente Promedio en el intervalo en Porcentaje: {}".format(str(df1.mean()["Coeficiente"])[:6]))

def coeficientes_intervalo(start_time, end_time,indices,df1,cups):
    coeficientes = []
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    horas = np.arange(start = horasInicio,stop = horasFin)
    for i,j in enumerate(horas):
        coeficientes.append([cups,str(10001+j)[-4:],"{:.6f}".format(df1["Coeficiente"][indices[i]]/100.0)])

    dfaux = pd.DataFrame(coeficientes,columns=["CUPS","hora","Coeficiente"])
    st.dataframe(dfaux,hide_index=True)

