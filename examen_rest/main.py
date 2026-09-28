from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import asynccontextmanager

import models
from database import engine, get_db

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    db = next(get_db())
    if db.query(models.Laptop).count() == 0:
        laptops_iniciales = [
            models.Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
            models.Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
            models.Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True)
        ]
        db.add_all(laptops_iniciales)
        db.commit()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"mensaje": "API del laboratorio de cómputo"}

@app.get("/laptops/disponibles", response_model=list[LaptopResponse])
def get_laptops_disponibles(db: Session = Depends(get_db)):
    return db.query(models.Laptop).filter(models.Laptop.disponible == True).all()

@app.get("/laptops", response_model=list[LaptopResponse])
def get_laptops(db: Session = Depends(get_db)):
    
    return db.query(models.Laptop).all()

@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def get_laptop(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.query(models.Laptop).filter(models.Laptop.id == laptop_id).first()
    if not laptop:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop

@app.post("/laptops", response_model=LaptopResponse)
def create_laptop(laptop: LaptopCreate, db: Session = Depends(get_db)):
    db_laptop = models.Laptop(
        marca=laptop.marca,
        modelo=laptop.modelo,
        ram_gb=laptop.ram_gb,
        disponible=True
    )
    db.add(db_laptop)
    db.commit()
    db.refresh(db_laptop)
    return db_laptop