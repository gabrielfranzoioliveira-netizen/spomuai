# ?? Lumia Spotify Auth Server

Servidor intermediário para autenticação OAuth do Spotify no robô Lumia.

## ? Setup Rápido (5 minutos)

### 1. Criar conta Upstash (OBRIGATÓRIO - gratuito)
1. Acesse https://console.upstash.com/
2. Login com GitHub ou Google
3. Clique "Create Database" ? Nome: `lumia` ? Região: São Paulo
4. Na aba "REST API", copie:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

### 2. Deploy no Vercel
```bash
npm i -g vercel  # se não tiver
cd spotify-auth-server
vercel
```

### 3. Configurar variáveis no Vercel
1. Acesse https://vercel.com/dashboard
2. Clique no projeto ? Settings ? Environment Variables
3. Adicione:
   - `UPSTASH_REDIS_REST_URL` = (sua URL)
   - `UPSTASH_REDIS_REST_TOKEN` = (seu token)
4. Clique "Save"

### 4. Redeploy
```bash
vercel --prod
```

## ?? Como funciona (Automático!)

```
[Robô] ? Mostra QR Code
    ?
[Celular] ? Escaneia ? Autoriza no Spotify
    ?
[Vercel] ? Recebe callback ? Salva no Upstash
    ?
[Robô] ? Polling detecta ? CONECTA AUTOMATICAMENTE!
```

**Não precisa falar nada depois de autorizar!** É automático igual a Alexa.
