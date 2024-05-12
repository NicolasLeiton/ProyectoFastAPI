from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from Componentes import Basededatos


ALGORITMO = "HS256"
LLAVE = "E847771A47DD909B0389ACF07382509C"
TOKEN_MINUTOS_EXPIRACION = 30

crypth = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def verificar_contra(contra:str, encrypt_contra:str) -> bool:
    return crypth.verify(contra, encrypt_contra)

def encriptar_contra(contra:str) -> str:
    return crypth.hash(contra)

def crear_token(id):
    access_token = {
        "sub": id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTOS_EXPIRACION)
    }
    return jwt.encode(access_token, LLAVE, algorithm=ALGORITMO)

def autenticar_usuario(email: str, contra: str):
    usuario = Basededatos.buscar_email(email)
    if not usuario:
        return False
    elif not verificar_contra(contra, usuario.get("password")):
        return False
    return usuario


#Verificar la validez de un token y devolver el usuario
async def verificar_token(token: str = Depends(oauth2)):
    error = HTTPException(status_code=401,
                            detail="No se pueden verificar las credenciales",
                            headers={"WWW-Authenticate": "Bearer"})

    try:
        token2 = jwt.decode(token, LLAVE, algorithms=[ALGORITMO])
        id = token2.get("sub")
        if id == None:
            raise error
    except JWTError:
        raise error
    
    return Basededatos.buscar_id(id)

async def verificar_permiso(usuario: dict = Depends(verificar_token)):
    error=HTTPException(status_code=401,
                            detail="No tienes permiso para realizar esta accion")
  
    permiso = usuario["permiso_modificar"]
    if permiso == True:
        return True
    else:
        raise error


