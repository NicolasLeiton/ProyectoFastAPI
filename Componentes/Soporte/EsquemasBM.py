from pydantic import BaseModel

class Empleado(BaseModel):
    id: str = None 
    email: str #Usado como otra Primary key
    nombres: str
    apellidos: str
    telefono: int
    puesto:str
    salario:float
    permiso_modificar: bool = False

class UserDB(Empleado):
    password: str
    

class Act_form(BaseModel):
    campo: str
    act: str

class Token(BaseModel):
    access_token: str
    token_type: str

def set_dict(emp) -> dict:
    return {
        "id" : str(emp["_id"]),
        "email": emp["email"],
        "nombres": emp["nombres"],
        "apellidos": emp["apellidos"],
        "telefono": emp["telefono"],
        "puesto": emp["puesto"],
        "salario": emp["salario"],
        "password": emp["password"],
        "permiso_modificar": emp["permiso_modificar"]
    }

def tupl_desprendible(emp, desp) -> list:
    return [
        str(desp["_id"]),
        desp["fecha_pago"],
        desp["hora_pago"],
        emp["nombres"],
        emp["apellidos"],
        desp["correo_enviado"],
        emp["puesto"],
        desp["salario_pagado"]
    ]



    


'''
datos = {
    "email": "admin@gmail",
    "nombres": "admin",
    "apellidos": "",
    "telefono": 3013213412,
    "puesto": "Administrador",
    "salario": 100000,
    "password": "admin123",
    "permiso_modificar": True
}
'''