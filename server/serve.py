import os
import subprocess
from pathlib import Path

from flask import Flask, render_template, url_for, send_file, request


def main():
    app = Flask('server', static_folder='server/static', template_folder='server/templates')

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

    @app.route('/sync')
    def synchronize():
        is_force = request.args.get('force')
        text = ''
        if is_force == 'True':
            result = subprocess.run(['git', 'fetch'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            text += result.stdout.decode('utf-8')
            result = subprocess.run(['git', 'reset', '--hard', 'origin/develop'],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            text += result.stdout.decode('utf-8')
        else:
            result = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            text += result.stdout.decode('utf-8')
        return render_template('operation.html.j2', output=text)

    app.run(host='0.0.0.0', port=8001)


if __name__ == '__main__':
    main()
