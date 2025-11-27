"""
Spotify OAuth Callback Handler para Vercel
Recebe o código do Spotify e armazena temporariamente
"""
from http.server import BaseHTTPRequestHandler
import json
import time
import os

# Armazenamento temporário em memória (Vercel serverless)
# Na prática, vamos usar KV storage ou retornar o código na página
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', [''])[0]
            
            # Página de sucesso que mostra o código para copiar
            # E também envia via postMessage para apps que suportam
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lumia - Spotify Conectado!</title>
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
        .container {{
            text-align: center;
            max-width: 500px;
        }}
        .success-icon {{
            font-size: 80px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #1DB954;
        }}
        p {{
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        .code-box {{
            background: rgba(255,255,255,0.1);
            border: 2px solid #1DB954;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }}
        .code {{
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            word-break: break-all;
            color: #1DB954;
            user-select: all;
        }}
        .copy-btn {{
            background: #1DB954;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
        }}
        .copy-btn:hover {{
            background: #1ed760;
            transform: scale(1.05);
        }}
        .copy-btn:active {{
            transform: scale(0.95);
        }}
        .instruction {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }}
        .instruction p {{
            font-size: 1em;
            margin-bottom: 10px;
        }}
        .copied {{
            background: #4CAF50 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Conectado!</h1>
        <p>Sua conta Spotify foi autorizada com sucesso.</p>
        
        <div class="instruction">
            <p>📱 <strong>Volte para o robô e diga:</strong></p>
            <p style="font-size: 1.3em; color: #1DB954;">"Lumia código conectado"</p>
        </div>
        
        <div class="code-box" style="display: none;">
            <p style="font-size: 0.9em; margin-bottom: 10px;">Código de autorização:</p>
            <div class="code" id="code">{code}</div>
            <button class="copy-btn" onclick="copyCode()">📋 Copiar Código</button>
        </div>
    </div>
    
    <script>
        // Salvar código no localStorage para o robô buscar
        const code = "{code}";
        const state = "{state}";
        
        // Enviar para o servidor armazenar
        fetch('/api/store?code=' + encodeURIComponent(code) + '&state=' + encodeURIComponent(state));
        
        function copyCode() {{
            navigator.clipboard.writeText(code);
            const btn = document.querySelector('.copy-btn');
            btn.textContent = '✓ Copiado!';
            btn.classList.add('copied');
            setTimeout(() => {{
                btn.textContent = '📋 Copiar Código';
                btn.classList.remove('copied');
            }}, 2000);
        }}
    </script>
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
