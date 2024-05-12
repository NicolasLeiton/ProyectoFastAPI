from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm

from os import getcwd
from apscheduler.schedulers.background import BackgroundScheduler

from Componentes import Basededatos, Autenticacion, GeneradorDesprendibles as GD
from Componentes.Soporte.EsquemasBM import *
from Componentes import Correos


app = FastAPI()
#documentacion swagger en /docs
#---------------------- Programar envio de correos ----------------------
scheduler = BackgroundScheduler()
scheduler.add_job(Correos.correos_masivos, 'cron', hour=23, minute=00) #Hora Colombia UTC-5
scheduler.start()

#---------------------- Autenticacion en la API ----------------------
@app.post("/login")
async def loggearse(formulario: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = Autenticacion.autenticar_usuario(formulario.username, formulario.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = Autenticacion.crear_token(user.get("id"))
    
    return Token(access_token=token, token_type="bearer")

#---------------------- Usuarios en general ----------------------
#Informacion del usuario
@app.get("/me", response_model=Empleado)
async def mi_informacion(usuario: dict = Depends(Autenticacion.verificar_token)):
    return Empleado(**usuario)

#Lista de los desprendibles del usuario
@app.get("/me/desprendibles")
async def mis_desprendibles(usuario: dict = Depends(Autenticacion.verificar_token)):
    desprendibles = Basededatos.desprendibles_usuario(usuario["id"])
    if desprendibles == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error en la base de datos")

    return desprendibles

#PDF del desprendible solicitado
@app.get("/me/desprendibles/{id}", response_class=FileResponse)
async def devolver_pdf(id:str, usuario: dict = Depends(Autenticacion.verificar_token)):
    desprendible = GD.generar_desprendible(id)
    if desprendible == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="No se ha encontrado el desprendible solicitado")
    
    return FileResponse(getcwd() + "/Archivos/Desprendible_pago.pdf")


#Actualizar una parte de tu informacion
@app.patch("/me/actualizarinfo")
async def actualizar_campo(actualizacion: Act_form, usuario: dict = Depends(Autenticacion.verificar_token)):
    if actualizacion.campo not in ["email", "telefono", "nombres", "apellidos"]: #Unicos campos que puedes modificar
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No existe, o no se puede modificar este campo")

    respuesta = Basededatos.acualizar_campo(usuario["id"], actualizacion)
    if respuesta == True:
        return "Campo actualizado correctamente"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=respuesta)

#Cambiar contraseña, requiere poner la anterior y la nueva
@app.patch("/me/cambiar_contrasena")
async def cambiar_contrasena(contra_actual, nueva_contra, usuario: dict = Depends(Autenticacion.verificar_token)):
    if Autenticacion.verificar_contra(contra_actual, usuario.get("password")) == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="La contraseña actual es incorrecta")
    elif contra_actual == nueva_contra:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La contraseña nueva no puede ser igual a la actual")
    else:
        actualizacion = Act_form(campo = "password", act= Autenticacion.encriptar_contra(nueva_contra))
        Basededatos.acualizar_campo(usuario.id, actualizacion)


#---------------------- Recursos Humanos ----------------------
#Añadir usuario a la base de datos
@app.post("/hr/contratar", status_code=status.HTTP_201_CREATED, response_model= Empleado)
async def contratar_empleado(empleado:UserDB, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    respuesta = Basededatos.agregar_empleado(empleado)
    if respuesta== False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return respuesta

#Buscar algun empleado por su email
@app.get("/hr/empleado/", response_model=Empleado)
async def info_empleado(empmail:str, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    emp = Basededatos.buscar_email(empmail)
    if emp == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error el usuario no existe")
    return Empleado(**emp)

#Devuelve la informacion del empleado solicitado
@app.get("/hr/{emp_id}", response_model=Empleado)
async def info_empleado(emp_id:str, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    emp = Basededatos.buscar_id(emp_id)
    if emp == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error el usuario no existe")
    return UserDB(**emp)

#Cambia toda la informacion de un usuario (obligatoriamente hay que pasarle todos los campos)
@app.put("/hr/{emp_id}/actualizar")
async def cambiar_datos(emp_id:str, empleado:Empleado, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    if empleado.id == None:
        empleado.id = emp_id

    respuesta = Basededatos.acualizar_empleado(empleado)
    if respuesta == True:
        return "Informacion del empleado actualizada correctamente"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=respuesta)

#Cambia alguna parte de la informacion de un usuario
@app.patch("/hr/{emp_id}/actualizar")
async def cambiar_datos(emp_id:str, actualizacion:Act_form, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    if actualizacion.campo not in ["email", "telefono", "nombres", "apellidos", "permiso_modificar", "salario", "puesto"]:
        #Lo unico que no esta permitido cambiar es la contraseña
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe, o no se puede modificar este campo")

    respuesta = Basededatos.acualizar_campo(emp_id, actualizacion)
    if respuesta == True:
        return "Campo actualizado correctamente"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=respuesta)

#Borrar de la base de datos a un usuario
@app.delete("/hr/{emp_id}/eliminar")
async def eliminar_empleado(emp_id:str, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    if Basededatos.borrar_empleado(None, emp_id) == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="El usuario no existe en la base de datos")
    return "Empleado eliminado correctamente"

#Borrar de la base de datos a un usuario (Pasando su correo)
@app.delete("/hr/delempleado/")
async def eliminar_empleado(empmail:str, permiso: bool = Depends(Autenticacion.verificar_permiso)):
    if Basededatos.borrar_empleado(empmail) == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="El usuario no existe en la base de datos")
    return "Empleado eliminado correctamente"


#---------------------- Prueba Correos ----------------------

@app.post("/testmails")
async def probar_envio_mails(permiso: bool = Depends(Autenticacion.verificar_permiso)):
    if Correos.correos_masivos()== False:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)
    
    return "Correos enviados"