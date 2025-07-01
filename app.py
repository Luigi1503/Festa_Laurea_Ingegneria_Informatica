from flask import Flask, render_template, request, redirect, url_for, send_file
import json
from datetime import datetime
import os
import requests
import base64

app = Flask(__name__)

CONFIRM_FILE = 'conferme.json'

def inizializza_file():
    if os.path.exists(CONFIRM_FILE):
        return  # già esiste, non fare nulla

    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPO')
    branch = 'master'

    if not token or not repo:
        print("Token o repo mancante, non posso inizializzare conferme.json")
        return

    api_url = f'https://api.github.com/repos/{repo}/contents/{CONFIRM_FILE}?ref={branch}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }

    r = requests.get(api_url, headers=headers)
    if r.status_code == 200:
        contenuto_base64 = r.json().get('content', '')
        contenuto = base64.b64decode(contenuto_base64).decode('utf-8')
        with open(CONFIRM_FILE, 'w') as f:
            f.write(contenuto)
        print("✔️ conferme.json scaricato da GitHub.")
    else:
        print("⚠️ conferme.json non trovato su GitHub. Creo file vuoto.")
        with open(CONFIRM_FILE, 'w') as f:
            json.dump([], f, indent=2)


def salva_su_github(file_path, token, repo, branch='master'):
    with open(file_path, 'rb') as f:
        contenuto = base64.b64encode(f.read()).decode('utf-8')

    api_url = f'https://api.github.com/repos/{repo}/contents/{file_path}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }

    # Verifica se esiste già (per ottenere lo SHA)
    r = requests.get(api_url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None

    dati = {
        'message': 'Aggiorno conferme.json',
        'content': contenuto,
        'branch': branch
    }
    if sha:
        dati['sha'] = sha

    r = requests.put(api_url, headers=headers, json=dati)
    return r.status_code in [200, 201]

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

    # Upload automatico su GitHub
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPO')
    if token and repo:
        salva_su_github(CONFIRM_FILE, token, repo)

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

@app.route('/download')
def scarica_conferme():
    if not os.path.exists(CONFIRM_FILE):
        return "Nessuna conferma disponibile."
    return send_file(CONFIRM_FILE, as_attachment=True)

if __name__ == '__main__':
    inizializza_file()  # 👈 scarica conferme.json se manca
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
