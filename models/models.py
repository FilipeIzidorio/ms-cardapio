from sqlalchemy import Column, Date, Enum, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import text
from db.database import Base
import enum


class TurnoEnum(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"


class Cardapio(Base):
    __tablename__ = "cardapios"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    data = Column(Date, nullable=False, index=True)

    # Listas de IDs vindos do MS-Estoque (Java)
    prato_principal_ids = Column(ARRAY(Integer), nullable=False, server_default=text("'{}'"))
    acompanhamento_ids  = Column(ARRAY(Integer), nullable=False, server_default=text("'{}'"))
    salada_ids          = Column(ARRAY(Integer), nullable=False, server_default=text("'{}'"))
    sobremesa_ids       = Column(ARRAY(Integer), nullable=False, server_default=text("'{}'"))
    bebida_ids          = Column(ARRAY(Integer), nullable=False, server_default=text("'{}'"))

    # Enum PostgreSQL (valores: manha, tarde, noite)
    turno = Column(Enum(TurnoEnum, name="turno_enum"), nullable=True)

    __table_args__ = (
        UniqueConstraint("data", "turno", name="uq_data_turno_cardapio"),
    )
