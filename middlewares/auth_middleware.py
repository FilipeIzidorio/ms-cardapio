from fastapi import Request, HTTPException, status
import requests

AUTH_URL = "https://1736e818cd2a.ngrok-free.app/api/v1/auth/validate-token/"

async def auth_filter(request: Request, call_next):
    """Middleware de autenticação centralizada."""
    rotas_publicas = ["/", "/docs", "/openapi.json", "/health"]

    if request.url.path in rotas_publicas:
        return await call_next(request)

    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )

    try:
        headers = {"Authorization": token}
        response = requests.get(AUTH_URL, headers=headers, timeout=5)

        if 200 <= response.status_code < 300:
            try:
                request.state.user = response.json()
            except Exception:
                request.state.user = None
            return await call_next(request)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao validar token"
        )
