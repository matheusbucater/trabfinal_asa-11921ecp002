from pydantic import BaseModel
from typing import List

class RequestIngrediente(BaseModel):
    nome:     str

class RequestPostReceita(BaseModel):
    titulo: str

class RequestPutReceita(BaseModel):
    titulo: str
    modo_de_preparo: str
    tempo_de_preparo: str

class RequestMedida(BaseModel):
    medida: str
