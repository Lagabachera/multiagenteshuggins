import subprocess
import os

# Definir el orden de los scripts a ejecutar
scripts = [
    "setup_project.py",
    "advanced_setup_project.py",
    "final_improvements.py"
]

def verificar_y_ejecutar_script(script):
    """Verifica si el script existe y lo ejecuta."""
    if os.path.exists(script):
        print(f"\nEjecutando {script}...")
        result = subprocess.run(["python3", script], capture_output=True, text=True)
        
        # Mostrar salida y posibles errores
        if result.returncode == 0:
            print(f"{script} ejecutado exitosamente.")
            print(result.stdout)
        else:
            print(f"Error al ejecutar {script}:")
            print(result.stderr)
    else:
        print(f"{script} no encontrado. Asegúrate de que el archivo existe en el directorio actual.")

def ejecutar_configuracion_completa():
    """Ejecuta todos los scripts en el orden correcto para configurar el proyecto completamente."""
    print("Iniciando configuración completa del proyecto...\n")
    for script in scripts:
        verificar_y_ejecutar_script(script)
    print("\nConfiguración completa del proyecto finalizada.")

if __name__ == "__main__":
    ejecutar_configuracion_completa()
