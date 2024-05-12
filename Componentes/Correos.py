import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

from Componentes.Soporte.Keys import *
from Componentes import Basededatos, GeneradorDesprendibles as GD

def enviar_correo(destinatario:str) ->bool:
    # Configura la API de SendGrid con tu clave API
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    adjunto_path = os.getcwd() +"/Archivos/Desprendible_pago.pdf"
    # Lee el contenido del archivo adjunto
    with open(adjunto_path, "rb") as file:
        adjunto_data = file.read()
    adjunto_encoded = base64.b64encode(adjunto_data).decode()

    # Crea el objeto adjunto
    adjunto = Attachment(
        FileContent(adjunto_encoded),
        FileName(os.path.basename(adjunto_path)),
        FileType("application/pdf"),
        Disposition("attachment")
    )

    # Crea el correo electrónico
    message = Mail(
        from_email="nicolas.leitonp@utadeo.edu.co",  
        to_emails=destinatario,
        subject="Pago automatico de nomina.",
        html_content="<p>Se ha generado un desprendible de pago automaticamente, de parte de su empresa, archivo adjunto a continuacion.</p>"
    )
    
    # Adjunta el archivo al correo electrónico
    message.attachment = adjunto

    try:
        # Envía el correo electrónico
        response = sg.send(message)
        print(response.status_code)
        return True
    except Exception as e:
        print(str(e))
        return False

# Ejemplo de uso

def correos_masivos():
    correos = Basededatos.Correos_Usuarios()
    if correos==False:
        print("ERROR EN LA BASE DE DATOS")
        return False

    for i in correos:
        id_desp = GD.insertar_desprendible(i["id"])
        GD.generar_desprendible(id_desp)
        if enviar_correo(i["email"]) == False:
            print("Error al enviar el correo a ", i["email"])
        else:
            print("Correo enviado correctamente a ", i["email"])


