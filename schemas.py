from datetime import date
from typing import Optional, List
from pydantic import BaseModel
import enum

# Enum para os turnos
class TurnoEnum(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"

# ---- Schemas principais ----
class CardapioBase(BaseModel):
    data: date
    prato_principal: str
    acompanhamento: str
    salada: str
    sobremesa: str
    bebida: str
    turno: Optional[TurnoEnum] = None

class CardapioCreate(CardapioBase):
    pass

class CardapioUpdate(CardapioBase):
    pass

class CardapioPartialUpdate(BaseModel):
    data: Optional[date] = None
    prato_principal: Optional[str] = None
    acompanhamento: Optional[str] = None
    salada: Optional[str] = None
    sobremesa: Optional[str] = None
    bebida: Optional[str] = None
    turno: Optional[TurnoEnum] = None

class CardapioOut(CardapioBase):
    id: int  # agora é int sequencial
    class Config:
        from_attributes = True

# ---- Integração opcional com MS2 (prepare) ----
class ItemPreparar(BaseModel):
    itemId: str
    quantidade: int

class PrepararRequest(BaseModel):
    itens: List[ItemPreparar]
