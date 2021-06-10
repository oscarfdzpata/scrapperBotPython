from django.core.management.base import BaseCommand

from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

from aplicaciones.scrapper_Amazon.utils import Chivato


#Modelo donde guardo los datos para scrappear
from aplicaciones.scrapper_Amazon.models import Producto

#Librerias necesario para el pdf
import os
from django.conf import settings
from django.template.loader import get_template
#from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

#Libreria para el envio de correo.
import smtplib
from aplicaciones.scrapper_Amazon import base
from email.mime.text import MIMEText
import threading
from email.mime.multipart import MIMEMultipart
from django.template.loader import render_to_string  #No la uso, uso el get template

#Libreria para el enviao de pushbullet
from pushbullet import Pushbullet

#libreria para scrapear datos de amazon
from bs4 import BeautifulSoup
import requests

#Libreria para que espere x segundos entre procesos
import time

class Command(BaseCommand):
    help = "collect jobs"
    # define logic of command
    def handle(self, *args, **options):

        chivato= Chivato()
        try:
                  

                #Prueba de scrapeo:
                #chivato.scrapeo('https://www.amazon.es/Edifier-Studio-R1280DB-2-0-Bluetooth/dp/B082DHWSRD/ref=pd_vtp_23_2/260-0138445-2194507?_encoding=UTF8&pd_rd_i=B082DHWSRD&pd_rd_r=d8af6bf1-d545-40be-97cc-607ef2614173&pd_rd_w=wl3tM&pd_rd_wg=VChjW&pf_rd_p=1e71e03f-9d81-496d-bc07-c33cadb56a3a&pf_rd_r=XBKSPC3ZSHTPMG3HRRWS&psc=1&refRID=XBKSPC3ZSHTPMG3HRRWS')

                #Comiena el blucle
                productos=Producto.objects.filter(activadp=True)
                
                for p in productos:
                    url=p.productoUrl
                    try:
                        chivato.scrapeo(url)
                        precio=chivato.precioProducto
                        #actualizo el precio en el registro
                        if float(p.precio) != float(precio):
                            p.precio=float(precio)
                            p.save()
                            print("\n actualizo el precio en el registro, ha cambiado el precio del producto desde el ultimo scrapeo")
                        if precio < p.precioMinimo:
                            #Enviamos el email y el pushbullet
                            
                            #Prueba de la clase Chivato en el envio de emial
                            #chivato.envioDeEmailRegistro(p.email.strip())
                            chivato.envioDeEmailRegistro(p.email.strip(),"Scrapper Amazon: Producto rebajado","bajado de precio")

                            #Prueba de de envio de mesaje con Pushbullet
                            chivato.envioDePushBulletRegistro("Tu producto ha bajado: " + str(chivato.precioProducto),chivato.nombreProducto,p.tokenPushbullet.strip())

                            if p.idtelegram.strip() !="" and p.idtelegram != None:         
                                print("\n Inicio del proceso de envio Telegram ")
                                cadena="Tu producto rastreado  {}, ha bajado de precio. Ya puedes comprarlo".format(chivato.nombreProducto)
                                #chivato.envioTelegram(p.idtelegram.strip(),"Tu producto rastreado ha bajado al precio marcado:")                       
                                chivato.envioTelegram(p.idtelegram.strip(),cadena)
                                chivato.envioTelegram(p.idtelegram.strip(),url)
                                print("\n Fin del proceso de envio Telegram ")


                    except Exception as e:
                        print(e)

                    print("\n Espero 5 segundos entre cada scrapeo")
                    time.sleep(5) # espera en segundos entre cada scrapeo


        except Exception as e:
            print(e)

        self.stdout.write( 'job complete' )
