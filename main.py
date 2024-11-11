# main.py

import gradio as gr
from agentes.agente_integracion_datos import AgenteIntegracionDatos
from agentes.agente_busqueda import AgenteBusqueda
from utils.memoria import Memoria

# Inicializar agentes y memoria
agente_datos = AgenteIntegracionDatos()
agente_busqueda = AgenteBusqueda()
memoria = Memoria()

def interactuar(mensaje):
    if "conectar" in mensaje.lower():
        nombre_db = mensaje.split(":")[1].strip()
        respuesta = agente_datos.conectar_db(nombre_db)
    elif "analizar archivo" in mensaje.lower():
        archivo = mensaje.split(":")[1].strip()
        respuesta = agente_datos.procesar_archivo_y_crear_tabla("mi_base", archivo)
    elif "buscar" in mensaje.lower():
        tabla, consulta = mensaje.split(":")[1].strip().split(",")
        respuesta = agente_busqueda.consulta_natural(tabla.strip(), consulta.strip())
    elif "historial" in mensaje.lower():
        respuesta = memoria.recuperar_historial()
    elif "buscar en historial" in mensaje.lower():
        palabra_clave = mensaje.split(":")[1].strip()
        respuesta = memoria.buscar_interacciones(palabra_clave)
    else:
        respuesta = "Comando no reconocido."

    # Almacenar la interacción en memoria
    memoria.almacenar_interaccion(mensaje, respuesta)
    return respuesta

# Configurar la interfaz de Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Agente Multiusos para Integración y Búsqueda de Datos")
    chatbot = gr.Chatbot()
    txt = gr.Textbox(placeholder="Escribe tu mensaje aquí...")
    submit = gr.Button("Enviar")
    submit.click(interactuar, txt, chatbot)

if __name__ == "__main__":
    demo.launch()
