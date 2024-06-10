
import chromadb

mi_diccionario = {"CB1": "Que los estudiantes hayan demostrado poseer y comprender conocimientos en un área de estudio que parte de la base de la educación secundaria general, y se suele encontrar a un nivel que, si bien se apoya en libros de texto avanzados, incluye también algunos aspectos que implican conocimientos procedentes de la vanguardia de su campo de estudio.",
  "CB2": "Que los estudiantes sepan aplicar sus conocimientos a su trabajo o vocación de una forma profesional y posean las competencias que suelen demostrarse mediante la elaboración y defensa de argumentos y la resolución de problemas dentro de su área de estudio",
  "CB3": "Que los estudiantes tengan la capacidad de reunir e interpretar datos relevantes (normalmente dentro de su área de estudio) para emitir juicios que incluyan una reflexión sobre temas relevantes de índole social, científica o ética",
  "CB4": "Que los estudiantes puedan transmitir información, ideas, problemas y soluciones a un público tanto especializado como no especializado",
  "CB5": "Que los estudiantes hayan desarrollado aquellas habilidades de aprendizaje necesarias para emprender estudios posteriores con un alto grado de autonomía",
  "CG10": "Conocimientos para la realización de mediciones, cálculos, valoraciones, tasaciones, peritaciones, estudios, informes, planificación de tareas y otros trabajos análogos de informática, de acuerdo con los conocimientos adquiridos según lo establecido en el apartado 5, anexo 2, de la resolución BOE-A",
  "CG11": "Capacidad para analizar y valorar el impacto social y medioambiental de las soluciones técnicas, comprendiendo la responsabilidad ética y profesional de la actividad del Ingeniero Técnico en Informática",
  "CG3": "Capacidad para diseñar, desarrollar, evaluar y asegurar la accesibilidad, ergonomía, usabilidad y seguridad de los sistemas, servicios y aplicaciones informáticas, así como de la información que gestionan",
  "CG4": "Capacidad para definir, evaluar y seleccionar plataformas hardware y software para el desarrollo y la ejecución de sistemas, servicios y aplicaciones informáticas, de acuerdo con los conocimientos adquiridos según lo establecido en el apartado 5, anexo 2, de la resolución BOE-A",
  "CG5": "Capacidad para concebir, desarrollar y mantener sistemas, servicios y aplicaciones informáticas empleando los métodos de la ingeniería del software como instrumento para el aseguramiento de su calidad, de acuerdo con los conocimientos adquiridos según lo establecido en el apartado 5, anexo 2, de la resolución BOE-A",
  "CG6": "Capacidad para concebir y desarrollar sistemas o arquitecturas informáticas centralizadas o distribuidas integrando hardware, software y redes de acuerdo con los conocimientos adquiridos según lo establecido en el apartado 5, anexo 2, de la resolución BOE-A",
  "CG8": "Conocimiento de las materias básicas y tecnologías, que capaciten para el aprendizaje y desarrollo de nuevos métodos y tecnologías, así como las que les doten de una gran versatilidad para adaptarse a nuevas situaciones",
  "CG9": "Capacidad para resolver problemas con iniciativa, toma de decisiones, autonomía y creatividad. Capacidad para saber comunicar y transmitir los conocimientos, habilidades y destrezas de la profesión de Ingeniero Técnico en Informática",
  "CIB4": "Conocimientos básicos sobre el uso y programación de los ordenadores, sistemas operativos, bases de datos y programas informáticos con aplicación en ingeniería",
  "CIB5": "Conocimiento de la estructura, organización, funcionamiento e interconexión de los sistemas informáticos, los fundamentos de su programación, y su aplicación para la resolución de problemas propios de la ingeniería.",
  "CIC6": "Capacidad para comprender, aplicar y gestionar la garantía y seguridad de los sistemas informáticos",
  "CSI2": "Capacidad para determinar los requisitos de los sistemas de información y comunicación de una organización atendiendo a aspectos de seguridad y cumplimiento de la normativa y la legislación vigente",
  "CSI5": "Capacidad para comprender y aplicar los principios de la evaluación de riesgos y aplicarlos correctamente en la elaboración y ejecución de planes de actuación",
  "RA1": "Conocer los fundamentos de un sistema operativo, sus componentes y los conceptos esenciales para la comprensión de los mismos",
  "RA2": "Conocer diversos sistemas operativos y entornos de operación (tradicionales, GUI, multimedia, etc.), sus diferencias y requisitos en términos de recursos",
  "RA3": "Conocer el problema de la integración de sistemas y determinar los requisitos de interoperabilidad",
  "RA4": "Instalar, configurar y operar un sistema operativo multiusuario",
  "RA5": "Razonar la necesidad de los sistemas operativos en los entornos de computación actuales",
  "RA6": "Explicar el papel del sistema operativo como interfaz entre el hardware y los programas de usuario",
  "RA7": "Diferenciar las más relevantes técnicas de planificación de tareas, tanto para sistemas batch, interactivos y de tiempo real",
  "RA8": "Comprender las técnicas generales de gestión de E/S y su relación con el sistema de archivos. Cada resultado del aprendizaje puede aparecer asociado a varias partes de la asignatura, tratándose en cada una de ellas según una óptica práctica, teórica o analítica, siendo el conjunto de las partes el que define el resultado final. Por ello, para superar la asignatura es necesario que no existan vacíos en ninguna de las formas de enfocar los resultados de aprendizaje",
  "TRU1": "Capacidad de análisis y síntesis",
  "TRU2": "Comunicación oral y escrita",
  "TRU3": "Capacidad de gestión de la información",
  "TRU4": "Capacidad de aprendizaje autónomo",
  "TRU5": "Capacidad para trabajar en equipo"}


# para pruebas utilizo la base de datos en memoria
chroma_client = chromadb.Client()


from chromadb.utils import embedding_functions as embedding_functions
eb = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

collection = chroma_client.get_or_create_collection(name="competencias", embedding_function=eb, metadata={"hnsw:space": "cosine"})


values_list = list(mi_diccionario.values())

index_values = list(mi_diccionario.keys())

json_array = [{'codigo': key, 'descripcion': value} for key, value in mi_diccionario.items()]


## estructura de una competencia:
# documento: JSON del codigo y la descripción como string
# metadatos: JSON del codigo y la descripción pero como pydict
# id: el id de la competencia (es autoincremental, pero claro, hay que tener el mismo ID en la BBDD relacional)

# añade las competencias a la colección
collection.add(
    documents = values_list,
    metadatas = json_array,
    ids = [str(i) for i in range(1, values_list.__len__() + 1)]
)


collection.count()

def add_one_competencia_to_dbv (competencia_data) :
    id = competencia_data['id']
    codigo = competencia_data['codigo']
    desc = competencia_data['descripcion']

    # añade las competencias a la colección
    collection.add(
        documents = [{"codigo": codigo, "descripcion": desc}],
        metadatas = [{"codigo": codigo, "descripcion": desc}],
        ids = [str(id)]
    )



# !!  Hay que pasar por esta función todas las competencias que salgan de la guia docente

# TODO cambiar los args de entrada -> el diccionario con codigo y descripicón
def search_competencia_in_dbv (competencia_data) :
    codigo = competencia_data[0]
    desc = competencia_data[1]

    comp_list = []

    results = collection.query(
        query_texts=[desc],
        n_results=5,
        include=['metadatas', 'documents', 'distances']
    )

    # devuelve el id de la competencia más similar
    id = results['ids'][0][0]
    results['distances']

    try:
        
        if results['distances'][0][0] < 0:
            # print("es la misma competencia, tiene el id", id)
            competencia_data.insert(0, id)
            return {"id": competencia_data[0], "codigo": competencia_data[1], "descripcion": competencia_data[2]}

        elif results['distances'][0][0] < 0.5:
            # print("La competencia más similar tiene el id:", id)
            competencia_data.insert(0, id)
            return {"id": competencia_data[0], "codigo": competencia_data[1], "descripcion": competencia_data[2]}

            ## TODO Devolver la información de esa competencia (el id) para la relación
            
        else:
            # TODO añadir la nueva competencia a la BBDD relacional
            # (esto le asocia un id autoincremental)
            # TODO hacer la búsqueda por el campo de texto, siempre será true pq la acabamos de añadir
            ## y obtenemos el id de esa competenccia
            ## TODO añadirla a la BBDDV con el nuevo ID obtenido
            # print ("No tiene na que ver, la añado nueva")
            competencia_data.insert(0, 0)
            return {"id": competencia_data[0], "codigo": competencia_data[1], "descripcion": competencia_data[2]}

    except:
        print("Algo ha ido mal")

# search_competencia_by_desc("Razonar la necesidad de los sistemas operativos en los entornos de computación actuales")

# ! estoy pensando que habría que relacionarlo con la asignatura que toque, pero es que pufff tremenda pereza



