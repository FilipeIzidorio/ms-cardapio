from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field
import enum


class TurnoEnum(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"


class CardapioBase(BaseModel):
    data: date
    prato_principal_ids: List[int] = Field(default_factory=list)
    acompanhamento_ids:  List[int] = Field(default_factory=list)
    salada_ids:          List[int] = Field(default_factory=list)
    sobremesa_ids:       List[int] = Field(default_factory=list)
    bebida_ids:          List[int] = Field(default_factory=list)
    turno: Optional[TurnoEnum] = None


class CardapioCreate(CardapioBase):
    pass


class CardapioUpdate(CardapioBase):
    pass


class CardapioPartialUpdate(BaseModel):
    data: Optional[date] = None
    prato_principal_ids: Optional[List[int]] = None
    acompanhamento_ids:  Optional[List[int]] = None
    salada_ids:          Optional[List[int]] = None
    sobremesa_ids:       Optional[List[int]] = None
    bebida_ids:          Optional[List[int]] = None
    turno: Optional[TurnoEnum] = None


class CardapioOut(CardapioBase):
    id: int

    model_config = {
        "from_attributes": True
    }
