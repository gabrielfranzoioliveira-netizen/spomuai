"""
Spotify OAuth Callback Handler para Vercel
Recebe o código do Spotify e armazena para polling
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import urllib.parse

# Upstash Redis (opcional - funciona sem também)
UPSTASH_URL = os.environ.get('UPSTASH_REDIS_REST_URL', '')
UPSTASH_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', '')

def store_code_upstash(state, code):
    """Armazena código no Upstash Redis (se configurado)"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return False
    try:
        key = f"spotify_code_{state}"
        url = f"{UPSTASH_URL}/set/{key}/{urllib.parse.quote(code)}?EX=300"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {UPSTASH_TOKEN}')
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"Upstash error: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', ['default'])[0]
            
            # Tentar armazenar no Upstash
            stored = store_code_upstash(state, code)
            
            # Página de sucesso - indica que AUTORIZAÇÃO foi feita
            # Mas a CONEXÃO será feita pelo robô automaticamente
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lumia - Autorização OK!</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{ text-align: center; max-width: 500px; }}
        .success-icon {{
            font-size: 100px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #1DB954; }}
        p {{ font-size: 1.2em; margin-bottom: 20px; opacity: 0.9; }}
        .instruction {{
            margin-top: 30px;
            padding: 25px;
            background: rgba(29, 185, 84, 0.2);
            border: 2px solid #1DB954;
            border-radius: 15px;
        }}
        .waiting {{
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
        .spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: #1DB954;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Autorizado!</h1>
        <p>Permissão do Spotify concedida com sucesso.</p>
        
        <div class="waiting">
            <span class="spinner"></span>
            <span>O robô está conectando automaticamente...</span>
        </div>
        
        <div class="instruction" style="margin-top: 20px;">
            <p style="font-size: 1em; opacity: 0.8;">
                📱 <strong>Pode fechar esta página.</strong>
            </p>
            <p style="font-size: 0.9em; opacity: 0.6; margin-top: 10px;">
                O robô vai avisar quando estiver pronto!
            </p>
        </div>
    </div>
</body>
</html>
"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        elif 'error' in params:
            error = params['error'][0]
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Erro - Lumia</title>
    <style>
        body {{
            background: #1a1a2e;
            color: white;
            font-family: Arial;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }}
        h1 {{ color: #ff6b6b; }}
    </style>
</head>
<body>
    <div>
        <h1>❌ Erro</h1>
        <p>{error}</p>
        <p>Tente novamente dizendo "Lumia cadastrar Spotify"</p>
    </div>
</body>
</html>
"""
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Missing code parameter')
