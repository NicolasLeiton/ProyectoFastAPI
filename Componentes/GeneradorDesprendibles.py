from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

from os import getcwd
from datetime import date, datetime, timezone, timedelta
# from Componentes.Soporte.EsquemasBM import Token
from Componentes import Basededatos


def fecha_colombia():
    hora = (datetime.now(timezone.utc)) - timedelta(hours=5)
    return hora

def formato_num(numero) -> str:
#Funcion que devuelve un numero con comilla de millones, punto de miles, y coma decimal
    num_list = list("{:,}".format(numero)) #Formato de python estandar; con coma en miles y punto decimal
    num_list.reverse()
    num_str=""
    punto=-1

    for i, num in enumerate(num_list):
        if num == ",":
            if i-punto == 8:
                num_list[i]="'" 
            else:
                num_list[i]="."

        elif num == ".":
            punto=i
            num_list[i]=","

        num_str=num_list[i]+num_str

    return num_str

def generar_archivo(id, fecha, hora, nombre, apellido, email, puesto, salario):
    #Funcion que crea un desprendible de pago en pdf

    sal_dia= formato_num(round(salario/30, 2))
    salario=formato_num(salario)
    # Crear el documento
    doc = SimpleDocTemplate(getcwd() + "/Archivos/Desprendible_pago.pdf", pagesize=letter, title=id)
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = estilos["Heading1"]
    estilo_parrafo = estilos["BodyText"]
    
    # Contenido del desprendible
    contenido = []
    #Titulo
    contenido.append(Paragraph("<b>CABITO S.A</b>", estilo_titulo))
    contenido.append(Paragraph("<br/><br/>", estilo_parrafo))
    
    #Informacion
    contenido.append(Paragraph("<b>Fecha del pago:</b> %s %s" % (fecha, hora), estilo_parrafo))
    contenido.append(Paragraph("<b>Nombre:</b> %s %s" % (nombre, apellido), estilo_parrafo))
    contenido.append(Paragraph("<b>Email enviado a:</b> %s" % email, estilo_parrafo))
    contenido.append(Paragraph("<b>Puesto:</b> %s" % puesto, estilo_parrafo))
    contenido.append(Paragraph("<b>Salario:</b> $%s" % salario, estilo_parrafo))
    contenido.append(Paragraph("<b>Pago día:</b> $%s" % sal_dia, estilo_parrafo))

    contenido.append(Paragraph("<br/><br/>", estilo_parrafo))
    contenido.append(Paragraph("<b>ID desprendible:</b> %s" % id, estilo_parrafo))
    
    # Generar el PDF
    doc.build(contenido)

# Ejemplo de uso
#generar_archivo("7awgd2g81ja92rfaef", "2024-05-11","06:12 pm", "Juan", "Pérez", "juan@example.com", "Desarrollador", 1300000)


def insertar_desprendible(id:str) -> bool:
    #Inserta la informacion del desprendible generado en la base de datos
    usuario=Basededatos.buscar_id(id)
    desprendible = {
        "id_usuario": usuario["id"],
        "salario_pagado": usuario["salario"],
        "correo_enviado": usuario["email"],
        "fecha_pago": fecha_colombia().strftime("%Y-%m-%d"),
        "hora_pago": fecha_colombia().strftime("%I:%M %p")
    }
    return Basededatos.guardar_desprendible(desprendible)


def generar_desprendible(id_desp:str):
    desprendible=Basededatos.buscar_desp(id_desp)
    if desprendible==False:
        return False
    
    generar_archivo(*desprendible)
    return True
