import os
import requests
from typing import Optional, Dict, List
from fastapi import HTTPException, status

# URL base do microsserviço de estoque (Java)
ESTOQUE_API_BASE = os.getenv("ESTOQUE_API_BASE", "https://ms-estoque.onrender.com")


def fetch_item(item_id: int) -> Optional[dict]:
    """
    Consulta o MS-Estoque para verificar se um item existe.
    Retorna o JSON do item se encontrado.
    Retorna None se o item não existir (404).
    Lança HTTPException 502 se o serviço estiver indisponível ou falhar.
    """
    url = f"{ESTOQUE_API_BASE}/estoque/{item_id}"
    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="MS-Estoque indisponível para validação"
        )

    if resp.status_code == 404:
        return None

    if 200 <= resp.status_code < 300:
        try:
            return resp.json()
        except ValueError:
            # Caso o MS-Estoque retorne sucesso sem corpo JSON
            return {}

    # Outros códigos = falha de integração
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Erro {resp.status_code} ao validar item {item_id} no MS-Estoque"
    )


def validate_ids(payload_dict: Dict[str, List[int]]):
    """
    Valida todas as listas de IDs enviadas.
    Exemplo de payload_dict:
    {
        "prato_principal_ids": [1, 2],
        "acompanhamento_ids": [3],
        "salada_ids": [4],
        "sobremesa_ids": [],
        "bebida_ids": [5, 9]
    }
    Se algum ID não existir no MS-Estoque, levanta HTTP 400 com a lista dos inválidos.
    """
    invalidos: List[Dict[str, int]] = []

    for campo, lista in payload_dict.items():
        if not lista:
            continue
        for item_id in lista:
            if fetch_item(item_id) is None:
                invalidos.append({"campo": campo, "id": item_id})

    if invalidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "mensagem": "IDs inválidos no MS-Estoque",
                "invalidos": invalidos
            }
        )
