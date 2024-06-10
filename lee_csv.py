import csv
import re
from descargar_pdf import descargar_pdf

filename = 'química.csv' # Reemplaza 'archivo.csv' con el nombre de tu archivo CSV

# Lee el archivo CSV y guarda los elementos de la columna número 5 en una lista
with open(filename, 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    grado = re.sub(r'\.csv', '', filename)
    enlaces = []
    for row in csvreader:
        enlaces.append(str(row[5])) # Los índices de las columnas empiezan desde 0, por lo que la columna 5 es el índice 4

for enlace in enlaces:
    descargar_pdf(enlace, f'./{grado}/')

print(grado) # Imprime la lista resultante
