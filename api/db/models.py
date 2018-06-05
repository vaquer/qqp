from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    id_profeco =  Column(String(10), nullable=False)


class Price(Base):
    __tablename__ = 'price'
    id = Column(Integer, primary_key=True)
    id_product = Column(ForeignKey('Product'), index=True)
    marca = Column(String(100), nullable=False)
    id_establecimiento = Column(String(10), nullable=False)
    establecimiento = Column(String(200), nullable=False)
    direccion = Column(String(500), nullable=True)
    colonia = Column(String(200), nullable=True)
    codigo_postal = Column(String(8), nullable=False, index=True)
    estado = Column(String(50), nullable=True)
    latitud = Column(String(30), nullable=False)
    longitud = Column(String(30), nullable=False)
    precio = Column(Numeric, nullable=False)
    fecha_observacion = Column(Date(), nullable=False, index=True)
    fecha_actualizacion = Column(Date(), nullable=False, default=datetime.now().date(), index=True)



# from sqlalchemy import create_engine
# engine = create_engine('postgresql+psycopg2://username:password@localhost:5432/mydb')
# Base.metadata.create_all(engine)