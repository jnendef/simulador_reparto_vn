### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
import base64

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

from datetime import datetime

# definicion de las funciones
def borrar(campo,valor):
    # st.session_state[campo].remove(valores)
    st.session_state[campo].pop(valor)
    return 

def resetear(campo):
    st.session_state[campo] = {}
    return

def actualizarValores(usuario,cups,infoElem):
    infoElem[usuario]=cups

    return infoElem

def camposDataframe(concepto, columnas):
    info = st.session_state[concepto]
    df = pd.DataFrame.from_dict(info,orient='index', columns=columnas)
    return df

# def obtenerCups(concepto,userId):
#     seleccion = st.session_state[concepto]
#     for j in seleccion:
#         if j[0].split("-")[0] == userId:
#             return j[1]
#     return ""

def escritura(archivo,cups,coeficiente):
    aux= ("\n"+cups+";{0:.6f}".format(coeficiente/100.0)).replace('.',',')
    archivo = archivo + aux
    return archivo

# Codigo de la app que se vera

st.markdown("# Resultados")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))

st.markdown("## Comunidad: "+str(st.session_state.nComunidad))
st.markdown("### Simulación para el Año: "+str(st.session_state.anyo))
st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

if st.session_state.idComunidad>0:
    try:
        datosUsr = []
        AddCups = False

        if st.sidebar.button("Preparar"):
            agente = Agente_MySql()
            sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
            usuarios = agente.ejecutar(sentenciaSQLusr)

            #st.write(usuarios)
            for i in usuarios:
                sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
                datos = agente.ejecutar(sentenciaSQLdatos)
                datosUsr.append((i[10],datos))
            st.session_state.usuariosCE = datosUsr
        tipologiaSB = {
            6:"Apartamento un adulto calefacción eléctrica",
            7:"Apartamento un adulto calefacción gas",
            9:"Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
            8:"Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
            12:"Piso dos adultos, calefacción gas y AC",
            10:"Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
        }
        datosUsr2 = st.session_state.usuariosCE
        listaUsCE = []
        listaIdUs = []
        for i in datosUsr2:
            aux = i[0].split("-")
            listaUsCE.append(aux[1]+"-"+tipologiaSB[int(aux[0])])
            listaIdUs.append(aux[1])
            
        cupsUsers = []
        usuarioElegido = st.selectbox("seleccione el usuario",listaUsCE,on_change=None)
        CupsUsuario = st.text_input("CUPS Usuario",max_chars=22)
        
        if st.button("Añadir CUPS"):
            indice = listaUsCE.index(usuarioElegido)
            # st.write(datosUsr2[indice][0])
            # st.write(st.session_state["cupsUsuarios"])
            actualizarValores(datosUsr2[indice][0],CupsUsuario,st.session_state["cupsUsuarios"])
        
        if st.button("Borrar CUPS"):
            indice = listaUsCE.index(usuarioElegido)
            borrar("cupsUsuarios",datosUsr2[indice][0])
            
        columns = ["CUPS"]
        dfCups = camposDataframe("cupsUsuarios",columns)
        st.dataframe(dfCups)

        listaUsr = []
        diccioUsr = {}
        redListaU = []

        descargable = ""
        if st.button("Preparar archivo"):
            mDatos = np.zeros((len(datosUsr2),len(datosUsr2[0][1]),4))
            for i in range(len(datosUsr2)):
                claveUsr = datosUsr2[i][0]
                listaUsr.append(claveUsr)
                if claveUsr not in redListaU:
                    redListaU.append(claveUsr)
                diccioUsr[claveUsr] = i
                for j in range(len(datosUsr2[i][1])):
                    for k,l in enumerate(datosUsr2[i][1][j]):
                        if k>2:
                            mDatos[i,j,k-3] = l

            Coeficientes = mDatos[:,:,1]

            for i in range(len(datosUsr2)):
                # cups = obtenerCups("cupsUsuarios",listaIdUs[i])
                cups = st.session_state["cupsUsuarios"][datosUsr2[i][0]]
                for j in mDatos[i,:,1]:
                    descargable = escritura(descargable,cups,j)
            
            st.download_button("Descarga", descargable[1:])

    except Exception as e:
        st.write("Realice una simulación para poder sacar el archivo con los coeficientes de reparto")
        st.write(e)

    