import requests
from bs4 import BeautifulSoup
import re
import csv


def main():
    #url = "https://www.uah.es/es/estudios/estudios-oficiales/grados/asignaturas/index.html?codPlan=G250"
    url = "https://www.uah.es/es/estudios/estudios-oficiales/grados/asignaturas/index.html?codCentro=210&codPlan=G581"
    #url = 'https://www.uah.es/es/estudios/estudios-oficiales/grados/asignaturas/index.html?codPlan=G660'
    #url = 'https://www.uah.es/es/estudios/estudios-oficiales/grados/asignaturas/index.html?codPlan=G343'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    h2_element = soup.find('h2', class_='title').text

    grado = limpia_grados(h2_element).strip()

    # Imprimimos el contenido del elemento h2 encontrado
    print(grado)

    # Buscamos todas las tablas con la clase "table-striped" y "table-bordered"
    tablas = soup.find_all('table', {'class': 'table table-striped table-bordered'})


# Podemos imprimir la cantidad de tablas encontradas
    print(f"Se encontraron {len(tablas)} tablas")

    with open(f'{grado.replace(" ", "_").lower()}.csv', 'w+', newline='', encoding='utf-8') as file:

# Y ahora podemos iterar sobre las filas de la tabla y guardar los enlaces como lo hicimos antes
        for tabla in tablas:

            elemento_anterior = tabla.find_previous_sibling()
            cuatri = re.sub(r'\D*', '', elemento_anterior.text)

            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 2:
                    asignatura = celdas[0].text.strip().capitalize()
                    idioma = celdas[1].text.strip()
                    enlace = celdas[2].find('a').get('href')
                    creditos = celdas[3].text.strip()
                    enlace_completo = f"https://www.uah.es{enlace}"
                    nombre, codigo = get_nombre_e_id(asignatura)
                    tipo = celdas[-1].text.strip().lower()
                    if tiene_numero(celdas[-1].text):
                        cuatri = re.sub(r'\D*', '',celdas[-1].text)
                        tipo = 'optativa'
                    #print(f"Grado: {grado.capitalize()} | Asignatura: {texto} | Créditos: {creditos} | Cuatrimestre: {cuatri} | Idioma: {idioma.lower()} | Enlace: {enlace_completo} | Tipo: {tipo} |ID: {codigo}")
                    # print(f"{grado.capitalize()}, {texto}, {creditos}, {cuatri}, {idioma.lower()}, {enlace_completo}, {tipo}, {codigo}")
                    file.write(f"{grado.capitalize()};{nombre};{creditos};{cuatri};{idioma.lower()};{enlace_completo};{tipo};{codigo}\n")

# separa el nombre de la asignatura y su ID
def get_nombre_e_id(nombre):
    texto, numero = re.split(r'\s-\s', nombre)
    return texto,numero

def limpia_grados(h2_element):
    grado = re.sub(r'GRADO EN \d*', '', h2_element)
    grado = re.sub(r'\d*', '', grado)
    grado = re.sub(r'-', '', grado.strip())
    return grado


# Utiliza una expresión regular para buscar patrones numéricos en el texto
# y devuelve True o False 
def tiene_numero(campo):
    patron_numerico = re.compile(r'\d+')
    return bool(patron_numerico.search(campo))

main()
