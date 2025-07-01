from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)

CONFIRM_FILE = 'conferme.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/conferma', methods=['POST'])
def conferma():
    nome = request.form.get('nome')
    cognome = request.form.get('cognome')

    nuova_conferma = {
        'nome': nome.strip(),
        'cognome': cognome.strip(),
        'timestamp': datetime.now().isoformat()
    }

    if not os.path.exists(CONFIRM_FILE):
        with open(CONFIRM_FILE, 'w') as f:
            json.dump([nuova_conferma], f, indent=2)
    else:
        with open(CONFIRM_FILE, 'r+') as f:
            dati = json.load(f)
            dati.append(nuova_conferma)
            f.seek(0)
            json.dump(dati, f, indent=2)

    return redirect(url_for('grazie'))

@app.route('/grazie')
def grazie():
    return "<h1>🎉 Grazie per aver confermato! Ci vediamo alla festa! 🍷</h1>"

@app.route('/conferme')
def mostra_conferme():
    if not os.path.exists(CONFIRM_FILE):
        return "Nessuna conferma ancora."
    with open(CONFIRM_FILE) as f:
        dati = json.load(f)
    return {'conferme': dati}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
