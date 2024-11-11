import subprocess
import os
import sys

def verificar_dependencias():
    """Verifica y actualiza todas las dependencias del proyecto."""
    print("Verificando dependencias...")
    subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"])
    print("Dependencias verificadas y actualizadas.")

def configurar_pre_commit():
    """Configura pre-commit hooks para mantener el estilo de código uniforme."""
    print("Configurando hooks de pre-commit...")
    config = """
repos:
-   repo: https://github.com/psf/black
    rev: stable
    hooks:
    - id: black
-   repo: https://github.com/pre-commit/mirrors-flake8
    rev: v3.9.2
    hooks:
    - id: flake8
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.812
    hooks:
    - id: mypy
    """
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(config)
    subprocess.run([sys.executable, "-m", "pre_commit", "install"])
    print("Hooks de pre-commit configurados correctamente.")

def limpieza_final():
    """Realiza una limpieza final de archivos temporales y de caché."""
    print("Realizando limpieza de archivos temporales...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo") or file == "__pycache__":
                os.remove(os.path.join(root, file))
    print("Limpieza de archivos temporales completada.")

def mejoras_finales():
    """Ejecuta todas las mejoras finales del proyecto."""
    print("Iniciando mejoras finales...")
    verificar_dependencias()
    configurar_pre_commit()
    limpieza_final()
    print("Mejoras finales completadas.")

if __name__ == "__main__":
    mejoras_finales()
