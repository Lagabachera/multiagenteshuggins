# agentes/agente_busqueda.py

import os
from sqlalchemy import create_engine, Table, MetaData, select
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

DATABASE_DIR = "databases"

class AgenteBusqueda:
    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
        self.nlp_model = pipeline("text2sql", model="Salesforce/grappa_large_jnt", use_auth_token=HUGGINGFACE_API_KEY)

    def conectar_db(self, nombre_db):
        db_path = os.path.join(DATABASE_DIR, f"{nombre_db}.db")
        if not self.engine:
            self.engine = create_engine(f"sqlite:///{db_path}")
        return f"Conectado a la base de datos '{nombre_db}' para búsqueda."

    def consulta_natural(self, nombre_tabla, consulta_texto):
        """Convierte una pregunta en lenguaje natural en una consulta SQL."""
        # Utiliza el modelo Hugging Face para convertir la consulta en SQL
        sql_query = self.nlp_model(consulta_texto)
        table = Table(nombre_tabla, self.metadata, autoload_with=self.engine)
        
        # Ejecutar la consulta y devolver los resultados
        try:
            results = self.engine.execute(sql_query).fetchall()
            return [dict(row) for row in results] if results else "No se encontraron resultados."
        except Exception as e:
            return f"Error en la ejecución de la consulta SQL: {e}"
