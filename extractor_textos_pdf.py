import json
import PyPDF2
import re
import nltk
from nltk.tokenize import word_tokenize


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
    elimiar = r'\dAprobada en Junta de Escuela el día 3 de junio de 2022'
    # Eliminar los caracteres no alfabéticos al principio y al final de la cadena
    return re.sub(elimiar, '', texto)



# Abre el archivo PDF
archivo = open('./ingeniería_en_sistemas_de_información/580006.pdf', 'rb')

# Crea un objeto de lectura del PDF
lector = PyPDF2.PdfReader(archivo)
contenido = ""
# Busca el marcador que indica el comienzo del encabezado
marcador = None
for i in range(len(lector.pages)):
    pagina = lector.pages[i]
    contenido += pagina.extract_text()


patron_inicial = r'\d\. COMPETENCIAS\n'
patron_final = r'\d\. CONTENIDOS\n'

match_ini = re.search(patron_inicial, contenido)
match_fin = re.search(patron_final, contenido)

contenido = contenido[match_ini.start()+len(str(match_ini))+1:match_fin.start()]

#print(contenido)

'''
patron_competencias = r'\b[A-Z]+\d{1,3}\b'

for match in re.finditer(patron_competencias, contenido):
    print(f"La palabra '{match.group()}' está en la posición {match.start()}")
'''
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


text_file = open("_prueba.txt", "w+", encoding='utf-8')
text_file.write(contenido)
text_file.close()

'''
print(archivo.name)
esto da como rsultado: ./ingeniería_en_sistemas_de_información/580006.pdf
puedo eliminar '.pdf' y luego el contenido hasta la última '/', así me quedo solo con el nombre del archivo
este nombre lo puedo usar para añadir las competencias a cada asignatura''' 


# este nombre también debería ser el de la asignatura
# oooo
# meter un nivel siuperior con el par 'asignatura:nombre'
with open('archivo.json', 'w+', encoding='utf-8') as f:
    json.dump(diccionario, f, indent=2, ensure_ascii=False)