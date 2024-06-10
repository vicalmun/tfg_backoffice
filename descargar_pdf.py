from base64 import b64decode
import codecs
import requests
from bs4 import BeautifulSoup
import re
from urllib import request
import os

#url = "https://www.uah.es/es/estudios/descarga-de-ficheros/?anio=2022-23&codAsig=580017&codPlan=G581"

# async def descargar_pdf(url, save_dir='./'):
def descargar_pdf(url, save_dir='./'):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

# Buscar los paneles

    if (soup.find('embed')):
        pdf1 = soup.find('embed')

        if pdf1.has_attr("title"):
            print(pdf1.attrs["title"])

        if pdf1.has_attr("src"):
            '''    text_file = open("sample.txt", "w+")
        n = text_file.write(pdf1.attrs["src"])
        text_file.close()
        b64 = re.sub(r'data:application/pdf;base64,', '', pdf1.attrs["src"])
        '''
            if not os.path.exists(save_dir):
                # Si el directorio no existe, lo crea
                os.makedirs(save_dir)
    
            with request.urlopen(pdf1.attrs["src"]) as response:
                data = response.read()

            with open(f'{save_dir}{pdf1.attrs["title"]}', "wb") as f:
                f.write(data)
                return pdf1.attrs['title'] # Nuevo: devuelve el nombre del archivo descargado
    else:
        print("no se ha encontrado informacion")

#descargar_pdf(url)


# esta es la etiqueta a buscar: <embed title="250080_2022-23_Historia de la Iglesia católica en el mundo contemporáneo.pdf" src="data...
# y en ese src está el PDF, a lo mejor directamente desde ahí puedo descargarlo
