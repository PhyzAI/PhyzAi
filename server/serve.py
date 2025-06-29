import os
import shlex
import subprocess
import threading
from collections import defaultdict
from pathlib import Path

from flask import Flask, render_template, url_for, send_file, request, redirect


def main():
    app = Flask('server', static_folder='server/static', template_folder='server/templates')

    procs: dict[int, subprocess.Popen] = {}
    proc_cache: dict[int, bytes] = defaultdict(lambda: b'')
    nextid = 1

    @app.route('/fs/', defaults={'path': '.'})
    @app.route('/fs/<path:path>')
    def enumerate_fs(path: str):
        p = Path(path)
        if not p.exists():
            return "This file does not exist on the server.", 404
        if p.is_dir():
            kwa: dict = {
                "files": []
            }
            if p.parent is not None:
                kwa['parent'] = str(p.parent)
                kwa['link_parent'] = url_for('enumerate_fs', path=str(p.parent))
            for filename in os.listdir(p):
                label = filename
                subpath = p / filename
                if subpath.is_dir():
                    label += '/'
                kwa['files'].append((label, url_for('enumerate_fs', path=str(subpath))))
            return render_template('fs.html.j2', path=path, **kwa), 200
        return send_file(p)

    @app.route('/')
    def homepage():
        return render_template('index.html.j2')

    def launch_proc(cmdline: list[str]) -> int:
        nonlocal nextid
        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
        this_id = nextid
        procs[this_id] = proc
        nextid += 1

        def watcher():
            for data in iter(proc.stdout.read, b''):
                proc_cache[this_id] += data
            proc.stdout.close()

        th = threading.Thread(target=watcher)
        th.daemon = True
        th.start()

        return this_id

    @app.route('/procmon/')
    def procmon():
        return render_template('operation.html.j2')

    @app.route('/git/<command>')
    def gitcmd(command: str):
        broke_command = shlex.split(command)
        result = launch_proc(['git'] + broke_command)
        return redirect(url_for('procmon', pid=result))

    @app.route('/proclog/<int:proc_id>')
    def get_proclog(proc_id: int):
        proc = procs.get(proc_id)
        if proc is None:
            return {
                "error": f"ProcID {proc_id} not found"
            }, 404
        exc = proc.poll()
        if exc is None:
            exc = False
        return {
            "exitcode": exc,
            "stdout": proc_cache[proc_id].decode('utf-8'),
        }

    app.run(host='0.0.0.0', port=8001, debug=True)


if __name__ == '__main__':
    main()
