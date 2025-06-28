import os
import subprocess
from pathlib import Path

from flask import Flask, render_template, url_for, send_file


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
        result = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return render_template('operation.html.j2', output=result.stdout.decode('utf-8'))

    app.run()


if __name__ == '__main__':
    main()
