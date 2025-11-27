"""
API para armazenar e recuperar códigos de autorização
Usa Vercel KV ou armazenamento em memória
"""
from http.server import BaseHTTPRequestHandler
import json
import os

# Armazenamento simples em arquivo (funciona no Vercel com /tmp)
CODES_FILE = '/tmp/spotify_codes.json'

def load_codes():
    try:
        if os.path.exists(CODES_FILE):
            with open(CODES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_codes(codes):
    try:
        with open(CODES_FILE, 'w') as f:
            json.dump(codes, f)
    except:
        pass

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        import time
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Armazenar código
        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', ['default'])[0]
            
            codes = load_codes()
            codes[state] = {
                'code': code,
                'timestamp': time.time()
            }
            save_codes(codes)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'stored'}).encode())
            return
        
        # Buscar código (polling do robô)
        if 'state' in params:
            state = params['state'][0]
            codes = load_codes()
            
            if state in codes:
                data = codes[state]
                # Verificar se não expirou (5 minutos)
                if time.time() - data['timestamp'] < 300:
                    # Remover após uso
                    del codes[state]
                    save_codes(codes)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'found',
                        'code': data['code']
                    }).encode())
                    return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'pending'}).encode())
            return
        
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Invalid request'}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
