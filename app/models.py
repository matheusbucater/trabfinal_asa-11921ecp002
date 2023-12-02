from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
import os
# definindo a URL para conexão no banco
url = URL.create(
    drivername='postgresql+psycopg2',
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASS'),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DATABASE'),
    port=os.getenv('POSTGRES_PORT')
)
#url = "postgresql+psycopg2://postgres:banco@localhost/postgres"

# nesse ponto são instanciados os objetos para conexão com o banco
engine  = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class IngredienteReceita(Base):
    __tablename__ = "ingrediente_receita",
    idIngrediente = Column(ForeignKey("ingrediente.id"), primary_key=True)
    idReceita     = Column(ForeignKey("receita.id"), primary_key=True)
    medida        = Column(String)
    ingrediente   = relationship("Ingrediente", back_populates="receitas")
    receita       = relationship("Receita", back_populates="ingredientes")


class Ingrediente(Base):
    __tablename__  = 'ingrediente'
    id             = Column(Integer, primary_key=True)
    nome           = Column(String)
    receitas       = relationship("IngredienteReceita", back_populates="ingrediente", cascade="all, delete-orphan")

class Receita(Base):
    __tablename__         = 'receita'
    id                    = Column(Integer, primary_key=True)
    titulo                = Column(String)
    modo_de_preparo       = Column(String, nullable=True)
    tempo_de_preparo      = Column(String, nullable=True)
    ingredientes          = relationship("IngredienteReceita", back_populates="receita", cascade="all, delete-orphan")

Base.metadata.create_all(engine)
