from Componentes.Soporte.ClienteDB import db_client
from Componentes.Soporte.EsquemasBM import *
from bson import ObjectId
from Componentes.Autenticacion import encriptar_contra
#---------------------- READ ----------------------
def buscar_id(id:str):
    try:
        emp_finded = set_dict(db_client.CompanyDB.empleados.find_one({"_id": ObjectId(id)}))
        return emp_finded
    except:
        return False
    
def buscar_email(email:str):
    try:
        emp_finded = set_dict(db_client.CompanyDB.empleados.find_one({"email": email}))
        return emp_finded
    except:
        return False
    
def buscar_desp(id_desp:str):
    try:
        desp_finded = db_client.CompanyDB.pagos.find_one({"_id": ObjectId(id_desp)})
        emp_finded = buscar_id(desp_finded["id_usuario"])
        
    except:
        return False
    salgo =tupl_desprendible(emp_finded, desp_finded)
    print(salgo)
    return salgo

def desprendibles_usuario(id:str):
    try:
        busqueda = db_client.CompanyDB.pagos.find({"id_usuario": id})
        desprendibles ={}
        for num, i in enumerate(busqueda):
            i["_id"] = str(i["_id"])
            del i["salario_pagado"]
            del i["correo_enviado"]
            del i["hora_pago"]
            desprendibles.update({num: i})

        if len(desprendibles)==0:
            return {"Error": "No se ha encontrado ningun desprendible"}

        return desprendibles
    except:
        return False
    
def Correos_Usuarios():
    try:
        busqueda = db_client.CompanyDB.empleados.find()
        correos = []
        for i in busqueda:
            correos.append({
                "id": str(i["_id"]),
                "email": i["email"]
                })
        return correos
    except:
            return False

#---------------------- CREATE ----------------------
def agregar_empleado(empleado:UserDB):
    if buscar_email(empleado.email) != False:
         #Verificar que no exista ese email
         return False

    emp_dict= dict(empleado) #Convertirlo en diccionario
    del emp_dict["id"] #borrar el id
    emp_dict["password"] = encriptar_contra(emp_dict["password"])

    try:
        id = db_client.CompanyDB.empleados.insert_one(emp_dict).inserted_id #Insertar y guardar id
        return Empleado(**buscar_id(id)) #Devolver el empleado añadido
    except:
        return False

def guardar_desprendible(info:dict):
    try:
        id_desp = db_client.CompanyDB.pagos.insert_one(info).inserted_id
        return id_desp 
    except:
        return False
#---------------------- UPDATE ----------------------
def acualizar_empleado(empnuevo:Empleado):
    if type(empnuevo.id) != str: #Evitar un dato tipo None
        return "Error: ID no valido"
    
    empactual = buscar_id(empnuevo.id)
    if empactual == False:
        return "Error: El empleado no existe"
    
    try:
        emp_dict = dict(empnuevo)
        del emp_dict["id"]
        emp_dict.update({"password":empactual.get("password")})
        
        db_client.CompanyDB.empleados.find_one_and_replace({"_id":ObjectId(empnuevo.id)},
                                                            emp_dict)
        return True
    except:
        return "Error inesperado"

def acualizar_campo(id:str, actualizacion:Act_form):
    if type(id) != str: #Evitar un dato tipo None
        return "Error: ID no valido"
    elif buscar_id(id) == False:
        return "Error: El empleado no existe"
    elif actualizacion.campo == "email":
        if buscar_email(actualizacion.act) != False:
            return "Error: El correo ingresado ya existe"
    elif actualizacion.campo in ["telefono", "salario"]:
        try:
            if actualizacion.campo == "telefono":
                actualizacion.act = int(actualizacion.act)
            else:
                actualizacion.act = float(actualizacion.act)
        except:
            return "Error: El tipo de dato no coincide"
    
    try:
        db_client.CompanyDB.empleados.update_one({"_id":ObjectId(id)}, 
                                                {"$set": {actualizacion.campo: actualizacion.act} })
  
        return True
    except:
        return "Error inesperado"


#---------------------- DELETE ----------------------
def borrar_empleado(email: str  = None, id: str = None) -> bool:
        #Recibe o el email o el id
        if id!= None:
            encontrado = db_client.CompanyDB.empleados.find_one_and_delete({"_id":ObjectId(id)})
        elif email != None:
            encontrado = db_client.CompanyDB.empleados.find_one_and_delete({"email": email})
        else:
            return False

        if not encontrado:
            return False
        
        return True

