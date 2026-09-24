from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    operator = "operator"
    readonly = "readonly"

class ApiUser(Base):
    __tablename__ = "api_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.readonly, nullable=False)

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), index=True, nullable=False)
    data_nascimento = Column(Date, index=True, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    telefone = Column(String(20), index=True, nullable=False)

    endereco = relationship("Address", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    parentes = relationship("Relationship", foreign_keys="[Relationship.user_id]", back_populates="usuario_origem")

class Address(Base):
    __tablename__ = "enderecos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    logradouro = Column(String(150), index=True, nullable=False)
    numero = Column(Integer, index=True, nullable=False)
    bairro = Column(String(100), index=True, nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String(10), nullable=False)

    usuario = relationship("User", back_populates="endereco")

    __table_args__ = (
        Index("idx_endereco_vizinhanca", "bairro", "logradouro", "numero"),
    )

class Relationship(Base):
    __tablename__ = "parentescos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    related_user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    grau = Column(String(50), nullable=False)

    usuario_origem = relationship("User", foreign_keys=[user_id], back_populates="parentes")
    usuario_destino = relationship("User", foreign_keys=[related_user_id])

    __table_args__ = (
        UniqueConstraint('user_id', 'related_user_id', name='uq_relacionamento'),
    )
