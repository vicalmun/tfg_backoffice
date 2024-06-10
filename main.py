import json
import streamlit as st
import pandas as pd
from pandas.core.frame import DataFrame
import time
import requests

import base64
from PyPDF2 import PdfReader
from io import StringIO
import aiofiles

import chromadb
import constants

from descargar_pdf import descargar_pdf

from chroma_y_la_busqueda_de_competencias import search_competencia_in_dbv, add_one_competencia_to_dbv

import re

from openai import OpenAI

#### some variables
file_is_send = False
is_export_file = False
pdf_text = ""
# final_text = ""
final_edited_text = ""


client = OpenAI(
    api_key="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"
)

####### INICIANDO ESTADOS #######


# Inicializo el estado de la variable 'txt_competencias_raw' vacía
if 'txt_competencias_raw' not in st.session_state:
    st.session_state['txt_competencias_raw'] = None


# La lista de competencias que tedría que analizar la función process_comp
if 'lista_comp' not in st.session_state:
    st.session_state['lista_comp'] = None

if 'nuevas_competencias' not in st.session_state:
    st.session_state['nuevas_competencias'] = None

if 'nuevas_competencias_added' not in st.session_state:
    st.session_state['nuevas_competencias_added'] = None

if 'url_guia_docente' not in st.session_state:
    st.session_state['url_guia_docente'] = None


### CHROMADB funcs

# Cliente de red (en local)
# Esto hace que la BBDD sea persistente
chroma_client = chromadb.HttpClient(host="localhost", port=8007)

## imprime por consola la lista de colecciones existentes en la bbddv
print(chroma_client.list_collections())

## coleccion de competencias que vamos a utilizar en este código
competenciasCollection = chroma_client.get_or_create_collection(name="competencias")

def primera_importacion (documents, metadatas, ids):
    competenciasCollection.add(
    documents= documents,
    metadatas= metadatas,
    ids= [str(i) for i in range(1, documents.len())]
    )


def contrasta_competencia(codigo, descripcion):
    competenciasCollection.add(
    documents = descripcion,
    metadatas = {"codigo" : codigo, "descripcion" : descripcion},
    ids = [str(i) for i in range(1, 137)]
)


#### some functions

def extract_pdf_txt(file):
    aux_pdf_text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        aux_pdf_text += page.extract_text()
    return aux_pdf_text


def process_comp():
    competencias_analizadas = []
    competencias_found = ""
    my_dictionary = eval(st.session_state['txt_competencias_raw'])

    for clave, valor in my_dictionary.items():
        # print(f"La clave es {clave} y el valor es {valor}")
        competencias_found += (f"{clave} - {valor}\n")
        # esto funciona, ahora anañizar cada una de las strings contra BBDD VEC

        # Generate a tuple with each key-value pair
        data = list([clave, valor])

        # Call the search_by_text function with the data tuple
        competencias_analizadas.append(search_competencia_in_dbv(data))


    ## nom devulve nada, pero guarda los resulsados en st.session_state['lista_comp']
    st.session_state['lista_comp'] = competencias_analizadas


def tipo_competencia(codigo):
    tipo_competencia = ""
    if codigo.startswith('CB'):
        tipo_competencia = 'Básica'
    elif codigo.startswith('CG'):
        tipo_competencia = 'General'
    elif codigo.startswith('CI'):
        tipo_competencia = 'Interna'
    elif codigo.startswith('TR'):
        tipo_competencia = 'Transversal'
    elif codigo.startswith('RA'):
        tipo_competencia = 'Resultado A'
    else:
        tipo_competencia = 'Desconocido'
    return tipo_competencia

def add_to_db():
    add_status = False
    competencias = st.session_state['nuevas_competencias']
    for competencia in competencias:
        tipo = tipo_competencia(competencia['codigo'])
        data_to_send = {
            "tipo_competencia": tipo,
            "codigo": competencia["codigo"],
            "descripcion": competencia["descripcion"]
        }
        print(json.dumps(data_to_send), "----- data to send")
        response = requests.post(constants.URL_API_COMPETENCIAS, data= json.dumps(data_to_send))

        if response.status_code == 200:
            # recupera la competencia añadida de la BBDD relacional
            ultima_competencia = requests.get(constants.URL_API_ULTIMA_COMPETENCIA).json()
            # Añade la competencia a la BBDD vectorial
            add_one_competencia_to_dbv(ultima_competencia)

            print(ultima_competencia)
            add_status = True
        else:
            print("Error en la petición", response.status_code)
            st.write("Error en la petición", response.status_code)
            add_status = False
            
    st.session_state['nuevas_competencias_added'] = add_status
            

def corrige_texto(pdf_txt):
    completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "user", "content": f"Corrige las faltas de gramatica del siguiente documento json: {match_text(pdf_txt)}."},
                ]
            )
    return completion.choices[0].message.content

# busqueda del texto

def limpia_texto(texto):
    # Patrón para eliminar los caracteres no alfabéticos al principio y al final
    patron = r'^[^a-zA-Z]*|[^a-zA-Z]*$'
    # Eliminar los caracteres no alfabéticos al principio y al final de la cadena
    return re.sub(patron, '', texto)


def busca_punto(texto):
    patron = r'^([\w\s]+)\.\s+'  # buscar palabras y espacios seguidos de un punto y final
    coincidencia = re.search(patron, texto)
    if coincidencia:
        subcadena = coincidencia.group(1)  # obtener el grupo 1 de la coincidencia
    else:
        subcadena = texto  # si no se encuentra el patrón, usar la cadena original
    
    return subcadena

## esto es bien guarro, pero es que no he sido capaz de encontrar la forma de eliminar el pie de página como tal de cada página
def quitar_pie_pagina_ad_oc(texto):
    elimiar = r'\dAprobada en Junta de Escuela el d[í\x80]a \d{1,2} de junio de\s{0,1}\d{0,4}'
    # Eliminar los caracteres no alfabéticos al principio y al final de la cadena
    return re.sub(elimiar, '', texto)

## vendría a llamarse 'busca competencias'
def match_text(contenido):
    """
    Esta función recibe un texto 'contenido' y busca las competencias y sus descripciones en el texto.
    
    Parámetros:
        - contenido (str): El texto en el que se buscarán las competencias y sus descripciones.
        
    Retorna:
        - diccionario (dict): Un diccionario que contiene las competencias como claves y sus descripciones como valores.
    """
    patron_inicial = r'\d\. COMPETENCIAS\n'
    patron_final = r'\d\. CONTENIDOS\n'

    # contenido = re.sub(r'\dAprobada en Junta de Escuela el d[í]a \d{1,2} de junio de \d{1,4}', '', contenido)

    match_ini = re.search(patron_inicial, contenido)
    match_fin = re.search(patron_final, contenido)

    contenido = contenido[match_ini.start()+len(str(match_ini))+1:match_fin.start()]
    patron_competencias = r'\b[A-Z]+\d{1,3}\s*-?\b'

    palabras = re.findall(patron_competencias, contenido)

    diccionario = {}
    for i in range(len(palabras)):
        if i == len(palabras) - 1:
            diccionario[palabras[i]] = quitar_pie_pagina_ad_oc(busca_punto(limpia_texto(contenido[contenido.index(palabras[i]) + len(palabras[i]):])).replace('\n', ' '))
        else:
            inicio = contenido.index(palabras[i]) + len(palabras[i])
            fin = contenido.index(palabras[i+1])
            diccionario[palabras[i]] = quitar_pie_pagina_ad_oc(busca_punto(limpia_texto(contenido[inicio:fin]).replace('\n', ' ')))

    print(diccionario)
    return diccionario


st.write("""
# Deconstructor de Guías Docentes
## Obtén la información de las guías docentes con simples pasos
""")

gd_url = st.text_input('Escribe la URL de la guia docente')
st.session_state['url_guia_docente'] = gd_url


uploaded_file = st.file_uploader("O bien carga aquí el archivo PDF", type="pdf", on_change=st.cache_resource.clear)


if uploaded_file and st.session_state['url_guia_docente'] is None:
    file_is_send = st.button('Procesar archivo')


if file_is_send or st.session_state['url_guia_docente']:
    with st.status("Processing data...", expanded=True) as status:
        if gd_url is not None and not file_is_send:
            # data online
            st.write("Accediendo a la URL...")
            time.sleep(1)
            st.write("Descargando la guía docente....")
            tmp_file_name = descargar_pdf(gd_url, './tmp/')
            time.sleep(1)
            st.write("Procesando el documento...")
            pdf_text = extract_pdf_txt('./tmp/' + tmp_file_name)
            
            st.session_state['txt_competencias_raw'] = corrige_texto(pdf_text)
            status.update(label="Process complete!", state="complete", expanded=False)


        if uploaded_file is not None and file_is_send:
        # data offline
            st.write("Decodificando PDF...")
            pdf_reader = PdfReader(uploaded_file)
            time.sleep(1)
            st.write("Leyendo las páginas...")
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            time.sleep(1)
            st.write("Buscando la información...")
            # TODO
            time.sleep(1)
            st.write("Procesando el documento...")
            st.session_state['txt_competencias_raw'] = corrige_texto(pdf_text)
            status.update(label="Process complete!", state="complete", expanded=False)

        # st.session_state['txt_competencias_raw'] = final_text

        ## TODO por cada uno de los varlores del diccionario mirar si hay algo parecido en la bbdd vectorial 
        ## si no hay añadir una nueva entrada, tanto en la vectorial como en la normal
        ## si hay algo parecido -> recuperar la parecida de la BBDD vectorial (id) y añadir la nueva competencia en la asignatra que toque + añadir convalidacion

    final_edited_text = st.text_area("Se han encontrado las siguientes competencias en el documento:", st.session_state['txt_competencias_raw'])


## Si no hay texto se puede introducir manualmente
else:
    st.divider()
    does_text_exists = st.text_area("Introduce el texto de las competencias", st.session_state['txt_competencias_raw'])
    if does_text_exists:
        st.session_state['txt_competencias_raw'] = does_text_exists
        st.button('Encontrar competencias', on_click=process_comp)


if final_edited_text != "":
    st.button('Encontrar competencias', on_click=process_comp)


if (st.session_state['lista_comp'] is not None) :
    if (len(st.session_state['lista_comp']) > 0):
        nuevas_competencias = []
        for competencia in  st.session_state['lista_comp']:
            if competencia['id'] == 0:
                nuevas_competencias.append(competencia)
        
        
        if len(nuevas_competencias) > 0:
            st.session_state['nuevas_competencias'] = nuevas_competencias
            st.write("Las competencias no registradas son:" )
            for c in  nuevas_competencias:
                st.write("", c['codigo'], c['descripcion'])

            st.divider()
            st.write("¿Deseas añadirlas a la BBDD?")
            is_export_file  = st.button('Añadir a BBDD', on_click=add_to_db)
            print("\n\n ----------------- ",is_export_file)
            if st.session_state['nuevas_competencias_added'] and st.session_state['nuevas_competencias_added'] is not None:
                st.write("Competencias añadidas correctamente")
            elif st.session_state['nuevas_competencias_added'] is not None and not st.session_state['nuevas_competencias_added']:
                st.error("Error al añadir las competencias")
        else:
            st.write("No hay competencias nuevas")



## TODO: filtro los RA? eso se puede saber mirándo el código de la competencia -> debería


# TODO: rehacer la parte para que sea más botnita cuando busque la competencia por URL