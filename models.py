from sqlalchemy import Column, String, Date, Enum, UniqueConstraint, Integer
from database import Base
import enum

class TurnoEnum(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    noite = "noite"

class Cardapio(Base):
    __tablename__ = "cardapios"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Sequencial
    data = Column(Date, nullable=False)
    prato_principal = Column(String, nullable=False)
    acompanhamento = Column(String, nullable=False)
    salada = Column(String, nullable=False)
    sobremesa = Column(String, nullable=False)
    bebida = Column(String, nullable=False)
    turno = Column(Enum(TurnoEnum), nullable=True)

    __table_args__ = (
        UniqueConstraint("data", "turno", name="uq_data_turno_cardapio"),
    )
