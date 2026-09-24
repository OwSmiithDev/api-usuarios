from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

class AddressSchema(BaseModel):
    logradouro: str
    numero: int
    bairro: str
    cidade: str
    estado: str
    cep: str
    model_config = ConfigDict(from_attributes=True)

class RelativeSchema(BaseModel):
    nome: str
    cpf: str
    grau: str

class NeighborSchema(BaseModel):
    nome: str
    cpf: str

class UserBase(BaseModel):
    nome: str
    data_nascimento: date
    cpf: str
    telefone: str

class UserResponse(UserBase):
    id: int
    endereco: Optional[AddressSchema]
    parentes: List[RelativeSchema] = []
    vizinhos: List[NeighborSchema] = []
    model_config = ConfigDict(from_attributes=True)

class UserSummary(BaseModel):
    id: int
    nome: str
    cpf: str
    model_config = ConfigDict(from_attributes=True)
