# utils/memoria.py

import json
import os
from datetime import datetime

MEMORY_FILE = "documents/memoria.json"

class Memoria:
    def __init__(self):
        # Verificar si el archivo de memoria existe; si no, crearlo
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def almacenar_interaccion(self, user_message, assistant_response):
        """Almacena la interacción entre el usuario y el asistente en el archivo de memoria."""
        with open(MEMORY_FILE, "r+", encoding="utf-8") as f:
            memoria = json.load(f)
            memoria.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response
            })
            f.seek(0)
            json.dump(memoria, f, ensure_ascii=False, indent=2)

    def recuperar_historial(self):
        """Recupera el historial completo de interacciones."""
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def buscar_interacciones(self, palabra_clave):
        """Recupera interacciones específicas que contienen una palabra clave en el mensaje del usuario."""
        historial = self.recuperar_historial()
        return [interaccion for interaccion in historial if palabra_clave.lower() in interaccion["user_message"].lower()]
