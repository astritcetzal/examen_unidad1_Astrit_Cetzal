import typing
import strawberry

@strawberry.type
class Instructor:
    nombre: str

@strawberry.type
class Taller:
    nombre: str
    instructor:Instructor
    cupo:int
    activo:bool

@strawberry.input
class AgregarTallerInput:
    nombre: str
    instructor: str  
    cupo: int
    activo: bool


taller_db = [
    Taller(
        nombre="Python para backend",
        instructor=Instructor(nombre="Ana López"),
        cupo=20,
        activo=True
    ),
    Taller(
        nombre="Introducción a Docker",
        instructor=Instructor(nombre="Carlos Ruiz"),
        cupo=15,    
        activo=False
    ),
    Taller(
        nombre="Consultas con GraphQL",
        instructor=Instructor(nombre="Ana López"),
        cupo=25,
        activo=True
    ),
]

#consultar
@strawberry.type
class Query:
    @strawberry.field
    def talleres(self) -> typing.List[Taller]:
        return taller_db

    @strawberry.field
    def taller(self, nombre: str) -> typing.Optional[Taller]:
        for item in taller_db:
            if item.nombre == nombre:
                return item
        return None
    @strawberry.field
    def talleres_activos(self) -> typing.List[Taller]:
        found = []
        for item in taller_db:
            if item.activo:  # Filtramos por el booleano
                found.append(item)
        return found

#Mutaciones
@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_taller(self, taller: AgregarTallerInput) -> Taller:
        new_taller = Taller(
            nombre=taller.nombre,
            instructor=Instructor(nombre=taller.instructor),
            cupo=taller.cupo,
            activo=taller.activo,
        )
        taller_db.append(new_taller)
        return new_taller

schema = strawberry.Schema(query=Query, mutation=Mutation)
