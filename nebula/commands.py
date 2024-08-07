# commands.py
import sys
import time
import traceback

import subprocess
import os
import importlib.resources

from watchdog.observers import Observer

from nebula.server import FileChangeHandler
HOST, PORT = "127.0.0.1", 40000


def start_server(host, port):
    global server_process
    global HOST, PORT
    HOST, PORT = host, port
    print(f"""
Starting development server at http://{host}:{port}/
Quit the server with CTRL-BREAK.
""")
    server_process = subprocess.Popen([sys.executable, '-c', 'from nebula.server import start_server; start_server(host, port)'])

    event_handler = FileChangeHandler(restart_server, (host, port))
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        if server_process:
            server_process.terminate()
            server_process.wait()


def restart_server():
    global server_process
    if server_process.poll() is None:
        server_process.terminate()
        server_process.wait()
    server_process = subprocess.Popen([sys.executable, '-c', 'from nebula.server import start_server; start_server(HOST, PORT)'])


def start_project(project_name):
    with importlib.resources.path('nebula', 'project_template') as template_dir:
        copy_template_contents(template_dir, os.getcwd(), project_name)

    os.rename(os.path.join(os.getcwd(), "project_name"), project_name)
    print(f"Created project '{project_name}' successfully.")


def copy_template_contents(src, dst, project_name):
    """
    Recursively copy template contents to destination directory,
    processing .py-tpl files by substituting placeholders.
    """
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if item == "__pycache__":
            continue

        elif os.path.exists(dst_path):
            raise ValueError(f"{dst_path} already exists")

        elif os.path.isdir(src_path):
            os.makedirs(dst_path, exist_ok=True)
            copy_template_contents(src_path, dst_path, project_name)
        elif item.endswith('.py'):
            with open(src_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                content = template_content.replace("{{ project_name }}", project_name)

            with open(dst_path, 'w', encoding='utf-8') as new_file:
                new_file.write(content)
