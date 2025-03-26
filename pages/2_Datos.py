### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
from geopy.geocoders import Nominatim 
from string import punctuation

import base64
import logging

import numpy as np
import pandas as pd

from pages.scripts.funcionesgrles import resetear
from pages.scripts.calculos import calcula2
from pages.pages_content.page2 import creacion_CE, instalacion_fv, instalacion_eo, confirmacion
from pages.pages_content.page2 import instalacion_bat, registro_usuarios, registro_coeficientes

logging.getLogger("geopy").setLevel(logging.ERROR)

#Creacion de un localizador de coordenadas
geolocator = Nominatim(user_agent="aplication")
if 'localizador' not in st.session_state:
    st.session_state.localizador = geolocator.geocode("Zaragoza")
    
# Comienza la pagina
st.title("DATOS")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))
st.info("Se deben rellenar todos los campos requeridos antes de la subida de datos y la simulación. Prestar atención a los avisos en cada pestaña")

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8= st.tabs(["Comunidad", "Fotovoltaicos","Eólicos", "Baterías", "Usuarios","Coeficientes", "Confirmación", "Simular"])

ce = False
fv = False
eo = False
gen = False
bt = False
usr = False
sub = False

location = None

with tab1:
    comunidadEnerg, dfComu, ce = creacion_CE(geolocator,ce)

with tab2:
    dfFV, numeroFV, fv = instalacion_fv(ce, fv)

with tab3:
    dfEO, numeroEO, eo = instalacion_eo(ce, eo)

with tab4:
    try:
        dfBat, numeroBat = instalacion_bat(ce, fv, eo, gen)

    except Exception as e:
        logging.error("En las baterías: ", exc_info=True)
        st.error("Error en la ejecución del programa, pruebe a ir a la pestaña de acceso, recargar la página y volver a ingresar los datos. Si el error persiste, consulte los logs o hable con el administrador.")
        
with tab5:
    if fv or eo:
        gen = True
    try:
        dfUs, numeroUsers, usr = registro_usuarios(ce, gen, usr)
    
    except Exception as e:
        logging.error("En los usuarios: ", exc_info=True)
        st.error("Error en la ejecución del programa, pruebe a ir a la pestaña de acceso, recargar la página y volver a ingresar los datos. Si el error persiste, consulte los logs o hable con el administrador.")

with tab6:
    try:
        registro_coeficientes(numeroUsers,comunidadEnerg)
    except Exception as e:
        logging.error("En los coeficinetes: ", exc_info=True)
        st.error("Error en la ejecución del programa, pruebe a ir a la pestaña de acceso, recargar la página y volver a ingresar los datos. Si el error persiste, consulte los logs o hable con el administrador.")

with tab7:
    datos=[comunidadEnerg, dfComu, ce, dfFV, numeroFV, dfEO, numeroEO, dfBat, numeroBat, gen, dfUs, numeroUsers, usr]
    try:
        confirmacion(datos)
    except Exception as e:
        logging.error("En la confirmación de los datos: ", exc_info=True)
        st.error("Error en la ejecución del programa, pruebe a ir a la pestaña de acceso, recargar la página y volver a ingresar los datos. Si el error persiste, consulte los logs o hable con el administrador.")
    

with tab8:

    st.info("Nota aclaratoria: La simulación sólo se debe ejecutar tras haber exportado los datos. Debe seleccionar el año del que quiere realizar la simulación y luego hacer click en el botón Simular.")
    try:
        st.markdown("""## Nombre de la comunidad: {}""".format(str(st.session_state.comunidades[-1][0])))
        simulable = True
    except:
        st.write()
        simulable = False

    date_year = st.number_input("Año de la simulación", disabled= not simulable and not st.session_state.envioInfo, value = int(dt.datetime.now().year), min_value=2020,step=1)
    

    if 'run_button' in st.session_state and st.session_state.run_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    if st.button('Simular', disabled=((not any(st.session_state.procesosCurso)) or st.session_state.saltoSimu or st.session_state.running), type="primary", key='run_button'):
        exitoSim = calcula2(st.session_state.procesosCurso,date_year)
        st.session_state.anyo = date_year
        st.session_state.saltoSimu = True
        
        if exitoSim:
            st.success("Puede ver los resultados yendo a los enlaces de Resultados Generales e Individuales de la barra lateral.")
            st.write("Momento de inicio del proceso: ", st.session_state.procesosCurso)
            
            a_zero = ["comunidades","usuarios","fotovolt","eolicos","baterias","usuariosCE"]
            for i in a_zero:
                resetear(i)