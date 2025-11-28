"""
API para armazenar e recuperar códigos de autorização
Usa Upstash Redis (gratuito) para persistência no Vercel serverless
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

# Upstash Redis - Configure estas variáveis no Vercel Dashboard
# Vá em: https://console.upstash.com/ -> Crie um banco Redis grátis -> Copie as credenciais
UPSTASH_URL = os.environ.get('UPSTASH_REDIS_REST_URL', '')
UPSTASH_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', '')

def upstash_set(key, value, expire_seconds=300):
    """Armazena valor no Upstash Redis com expiração"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return False
    try:
        url = f"{UPSTASH_URL}/set/{key}/{urllib.parse.quote(value)}?EX={expire_seconds}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {UPSTASH_TOKEN}')
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception as e:
        print(f"Upstash SET error: {e}")
        return False

def upstash_get(key):
    """Busca valor no Upstash Redis"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        url = f"{UPSTASH_URL}/get/{key}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {UPSTASH_TOKEN}')
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        return data.get('result')
    except Exception as e:
        print(f"Upstash GET error: {e}")
        return None

def upstash_del(key):
    """Remove valor do Upstash Redis"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return False
    try:
        url = f"{UPSTASH_URL}/del/{key}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {UPSTASH_TOKEN}')
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        import urllib.parse
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Verificar se Upstash está configurado
        if not UPSTASH_URL or not UPSTASH_TOKEN:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Upstash not configured',
                'help': 'Configure UPSTASH_REDIS_REST_URL e UPSTASH_REDIS_REST_TOKEN no Vercel'
            }).encode())
            return
        
        # Armazenar código
        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', ['default'])[0]
            
            key = f"spotify_code_{state}"
            success = upstash_set(key, code, 300)  # 5 minutos
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'stored' if success else 'failed',
                'state': state
            }).encode())
            return
        
        # Buscar código (polling do robô)
        if 'state' in params:
            state = params['state'][0]
            key = f"spotify_code_{state}"
            
            code = upstash_get(key)
            
            if code:
                # Remover após uso
                upstash_del(key)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'found',
                    'code': code
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
