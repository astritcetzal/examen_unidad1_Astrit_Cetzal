from fastapi import FastAPI, Depends, HTTPException
import database
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from pydantic import BaseModel
import models


#modelos
class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int

class LaptopResponse(BaseModel):
     id: int
     marca: str
     modelo: str
     ram_gb: int
     disponible: bool

     class Config:
        from_attributes = True  

# Manejo del ciclo de vida de la app -> Crea tablas e inserta datos iniciales
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea la tabla si no existe
    models.Base.metadata.create_all(bind=database.engine)
    
    DB = database.SessionLocal()
    
    cantidad_laptops = DB.query(models.Laptop).count()
    
    if cantidad_laptops == 0:
        laptop1 = models.Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True)
        laptop2 = models.Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False)
        laptop3 = models.Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True)
        
        DB.add(laptop1)
        DB.add(laptop2)
        DB.add(laptop3)
        
        #    guardamos los cambios
        DB.commit()
        
    DB.close()
    
    yield

app = FastAPI(lifespan=lifespan)

# LOS 5 Endpoints
@app.get("/")
def leer_raiz():
    return {"mensaje": "API del laboratorio de Computo"}


@app.get("/laptops", response_model=list[LaptopResponse])
def obtener_laptops(DB: Session = Depends(database.get_db)):
    return DB.query(models.Laptop).all()

@app.get("/laptops/disponibles", response_model=list[LaptopResponse])
def obtener_laptops_disponibles(DB: Session = Depends(database.get_db)):
    return DB.query(models.Laptop).filter(models.Laptop.disponible == True).all()


@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def obtener_laptop(laptop_id: int, DB: Session = Depends(database.get_db)):
    laptop = DB.query(models.Laptop).filter(models.Laptop.id == laptop_id).first()
    if not laptop:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops", response_model=LaptopResponse)
def crear_laptop(laptop: LaptopCreate, DB: Session = Depends(database.get_db)):
    nueva_laptop = models.Laptop(
        marca=laptop.marca,
        modelo=laptop.modelo,
        ram_gb=laptop.ram_gb
    )
    DB.add(nueva_laptop)
    DB.commit()
    DB.refresh(nueva_laptop) 
    return nueva_laptop