import os
import json
import subprocess

# Variables de Configuración
project_name = "multi_agents_app"
virtual_env_name = "env"  # Nombre del entorno virtual
requirements_file = "requirements.txt"
dev_requirements_file = "requirements-dev.txt"
vscode_dir = ".vscode"
launch_json_path = os.path.join(vscode_dir, "launch.json")
tasks_json_path = os.path.join(vscode_dir, "tasks.json")
settings_json_path = os.path.join(vscode_dir, "settings.json")

# Función de Configuración para VS Code
def create_vscode_configs():
    os.makedirs(vscode_dir, exist_ok=True)
    
    # Configuración de launch.json
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Ejecutar main.py",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "python": "${command:python.interpreterPath}",
                "console": "integratedTerminal",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}",
                    "HUGGINGFACE_API_KEY": "${env:HUGGINGFACE_API_KEY}"
                },
                "justMyCode": True,
                "preLaunchTask": "Lint and Fix",
                "args": [],
                "cwd": "${workspaceFolder}",
                "envFile": "${workspaceFolder}/.env"
            }
        ]
    }
    with open(launch_json_path, "w") as f:
        json.dump(launch_config, f, indent=2)
    print(f"{launch_json_path} configurado.")

    # Configuración de tasks.json
    tasks_config = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Lint and Fix",
                "type": "shell",
                "command": f"./{virtual_env_name}/bin/flake8 ${{workspaceFolder}} && ./{virtual_env_name}/bin/black ${{workspaceFolder}} && ./{virtual_env_name}/bin/pylint ${{workspaceFolder}}",
                "group": {
                    "kind": "build",
                    "isDefault": True
                },
                "problemMatcher": ["$flake8"],
                "runOptions": {
                    "runOn": "folderOpen"
                }
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": f"./{virtual_env_name}/bin/pytest",
                "group": {
                    "kind": "test",
                    "isDefault": True
                },
                "problemMatcher": ["$pytest"]
            }
        ]
    }
    with open(tasks_json_path, "w") as f:
        json.dump(tasks_config, f, indent=2)
    print(f"{tasks_json_path} configurado.")

    # Configuración de settings.json
    settings_config = {
        "python.envFile": "${workspaceFolder}/.env",
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports": True
        },
        "python.formatting.provider": "black",
        "python.linting.flake8Enabled": True,
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.linting.mypyEnabled": True
    }
    with open(settings_json_path, "w") as f:
        json.dump(settings_config, f, indent=2)
    print(f"{settings_json_path} configurado.")
