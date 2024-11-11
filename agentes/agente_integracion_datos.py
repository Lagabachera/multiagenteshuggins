# agentes/agente_integracion_datos.py

import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from transformers import pipeline
from dotenv import load_dotenv
import pandas as pd
from PyPDF2 import PdfReader
import cv2
from PIL import Image
import pytesseract

# Cargar variables de entorno
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Configuración de directorios
DATABASE_DIR = "databases"
DOCUMENTS_DIR = "documents"

class AgenteIntegracionDatos:
    def __init__(self):
        self.engines = {}  # Diccionario para gestionar conexiones a múltiples bases de datos
        self.metadata = MetaData()  # Metadatos de SQLAlchemy para la creación dinámica de tablas
        self.models = {}  # Diccionario para cargar y almacenar modelos de Hugging Face

    # -----------------------------
    # Funciones de Configuración
    # -----------------------------

    def conectar_db(self, nombre_db):
        """Conecta o crea una nueva base de datos SQLite local."""
        db_path = os.path.join(DATABASE_DIR, f"{nombre_db}.db")
        if nombre_db not in self.engines:
            os.makedirs(DATABASE_DIR, exist_ok=True)
            self.engines[nombre_db] = create_engine(f"sqlite:///{db_path}")
        return f"Conectado a la base de datos '{nombre_db}'."

    def cargar_modelo_hf(self, modelo="distilbert-base-uncased"):
        """Carga un modelo de Hugging Face para análisis de texto."""
        if modelo not in self.models:
            try:
                self.models[modelo] = pipeline("text-classification", model=modelo, use_auth_token=HUGGINGFACE_API_KEY)
                return f"Modelo '{modelo}' cargado."
            except Exception as e:
                return f"Error al cargar el modelo '{modelo}': {str(e)}"
        return f"Modelo '{modelo}' ya está cargado."

    # -----------------------------
    # Funciones de Extracción de Datos
    # -----------------------------

    def extraer_datos_archivo(self, archivo):
        """Determina el tipo de archivo y dirige al método de extracción correspondiente."""
        extension = os.path.splitext(archivo)[1].lower()
        if extension == ".pdf":
            return self.extraer_texto_pdf(archivo)
        elif extension == ".csv":
            return self.extraer_datos_csv(archivo)
        elif extension in [".jpg", ".jpeg", ".png"]:
            return self.extraer_texto_imagen(archivo)
        elif extension in [".mp4", ".avi"]:
            return self.extraer_texto_video(archivo)
        else:
            return "Formato de archivo no soportado."

    def extraer_texto_pdf(self, archivo):
        """Extrae texto de cada página de un archivo PDF."""
        try:
            reader = PdfReader(archivo)
            return "".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            return f"Error al procesar PDF: {str(e)}"

    def extraer_datos_csv(self, archivo):
        """Lee un archivo CSV y lo convierte en una lista de diccionarios."""
        try:
            return pd.read_csv(archivo).to_dict(orient="records")
        except Exception as e:
            return f"Error al procesar CSV: {str(e)}"

    def extraer_texto_imagen(self, archivo):
        """Extrae texto de una imagen utilizando OCR (Optical Character Recognition)."""
        try:
            image = cv2.imread(archivo)
            return pytesseract.image_to_string(image)
        except Exception as e:
            return f"Error al procesar imagen: {str(e)}"

    def extraer_texto_video(self, archivo):
        """Extrae texto de frames seleccionados de un video mediante OCR."""
        try:
            texto = ""
            cap = cv2.VideoCapture(archivo)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            step = max(1, frame_count // 10)
            for i in range(0, frame_count, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    texto += pytesseract.image_to_string(frame)
            cap.release()
            return texto
        except Exception as e:
            return f"Error al procesar video: {str(e)}"

    # -----------------------------
    # Funciones de Análisis y Almacenamiento
    # -----------------------------

    def analizar_texto_hf(self, texto, modelo="distilbert-base-uncased"):
        """Analiza texto utilizando un modelo de Hugging Face."""
        if modelo not in self.models:
            cargar_resultado = self.cargar_modelo_hf(modelo)
            if "Error" in cargar_resultado:
                return cargar_resultado
        try:
            return self.models[modelo](texto)
        except Exception as e:
            return f"Error al analizar texto: {str(e)}"

    def analizar_datos_y_crear_tablas(self, nombre_db, data, nombre_tabla):
        """Analiza datos y crea una tabla en la base de datos con columnas basadas en el contenido."""
        self.conectar_db(nombre_db)
        engine = self.engines[nombre_db]

        try:
            columns = [Column('id', Integer, primary_key=True)]
            for key in data[0].keys():
                columns.append(Column(key, String))

            new_table = Table(nombre_tabla, self.metadata, *columns)
            self.metadata.create_all(engine)

            with engine.connect() as conn:
                conn.execute(new_table.insert(), data)

            return f"Tabla '{nombre_tabla}' creada y datos insertados en la base de datos '{nombre_db}'."
        except SQLAlchemyError as e:
            return f"Error al crear tabla: {str(e)}"

    def procesar_archivo_y_crear_tabla(self, nombre_db, archivo, modelo_hf="distilbert-base-uncased"):
        """Procesa un archivo, analiza texto con Hugging Face, y crea una tabla con los datos procesados."""
        datos = self.extraer_datos_archivo(archivo)
        
        if isinstance(datos, str):  # Si es texto, se analiza con Hugging Face
            resultados_hf = self.analizar_texto_hf(datos, modelo_hf)
            if isinstance(resultados_hf, str):
                return resultados_hf  # Retorna error si hubo un fallo en la carga o análisis
            datos_procesados = [{"texto_original": datos, "anotacion": resultado['label'], "confianza": resultado['score']} for resultado in resultados_hf]
        elif isinstance(datos, list):  # Si es lista de diccionarios (ej. CSV), se inserta directamente
            datos_procesados = datos
        else:
            return "Formato de archivo o datos no soportado."

        nombre_tabla = os.path.splitext(os.path.basename(archivo))[0]
        return self.analizar_datos_y_crear_tablas(nombre_db, datos_procesados, nombre_tabla)

    # -----------------------------
    # Funciones de Gestión de Flujos de Trabajo
    # -----------------------------

    def definir_flujo_trabajo(self, nombre_db, nombre_tabla_origen, nombre_tabla_destino, columna_relacion):
        """Define un flujo de trabajo entre tablas mediante una clave foránea."""
        self.conectar_db(nombre_db)
        engine = self.engines[nombre_db]

        try:
            table_destino = Table(nombre_tabla_destino, self.metadata, autoload_with=engine)
            new_column = Column(columna_relacion, Integer, ForeignKey(f"{nombre_tabla_origen}.id"))
            new_column.create(table_destino)
            return f"Flujo de trabajo creado: '{nombre_tabla_origen}' -> '{nombre_tabla_destino}' en '{nombre_db}'."
        except SQLAlchemyError as e:
            return f"Error al definir flujo de trabajo: {str(e)}"

    # -----------------------------
    # Funciones de Búsqueda
    # -----------------------------

    def buscar_en_tabla(self, nombre_db, nombre_tabla, filtro=None):
        """Realiza una búsqueda en una tabla utilizando filtros específicos."""
        self.conectar_db(nombre_db)
        engine = self.engines[nombre_db]

        try:
            table = Table(nombre_tabla, self.metadata, autoload_with=engine)
            query = table.select()

            if filtro:
                for key, value in filtro.items():
                    query = query.where(table.c[key] == value)

            results = engine.execute(query).fetchall()
            return [dict(row) for row in results] if results else "No se encontraron resultados."
        except SQLAlchemyError as e:
            return f"Error al realizar búsqueda: {str(e)}"
