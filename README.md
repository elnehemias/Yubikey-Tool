# Tubikey-Tool
Diseño e Integración de Skills Agenticas en una API desarrollada con FastAPI

==========================================================
 YUBIKEY PROVISIONER - INSTRUCCIONES DE EJECUCION
==========================================================

QUE ES
------
App local (FastAPI) para aprovisionar YubiKeys:
  - Eventbrite OTP: configura Yubico OTP en un slot, guarda un CSV
    por BMS y agrega el registro a un Excel.
  - Reset FIDO2: reinicia FIDO2 y limpia PIV, OATH, OpenPGP y OTP.
  - Agente IA (Gemini): ejecuta las mismas acciones desde un chat.

ARCHIVOS
------------------------------------------------
  app.py            -> servidor backend (FastAPI)
  index.html        -> interfaz web
  iniciar.bat       -> lanzador para Windows
  requirements.txt  -> lista de librerias (opcional, ver paso 2)


REQUISITOS PREVIOS
------------------
  - Windows 10/11
  - Python 3.9 o superior
      * Al instalar, marca la casilla "Add Python to PATH".
  - Una YubiKey conectada por USB
  - Permisos de Administrador (el .bat los solicita solo)
  - Para el Agente IA: una API Key de Gemini
      (gratis en https://aistudio.google.com/apikey)


LIBRERIAS NECESARIAS
--------------------
  fastapi          -> framework web del backend
  uvicorn          -> servidor que ejecuta la app
  openpyxl         -> lectura/escritura del Excel
  google-genai     -> cliente de Gemini (agente IA)
  yubikey-manager  -> instala el comando "ykman" que usa la app

  (pydantic se instala automaticamente junto con fastapi.
   csv, os, subprocess, threading y datetime ya vienen con Python.)


PASO A PASO
-----------
1) Abre una terminal (CMD o PowerShell) en la carpeta del proyecto:

       cd C:\ruta\a\la\carpeta

2) Instala las librerias. Opcion A:

       pip install -r requirements.txt

   Opcion B:

       pip install fastapi uvicorn openpyxl google-genai yubikey-manager

3) Verifica que ykman quedo disponible:

       ykman --version

   Si dice "no se reconoce el comando", cierra y vuelve a abrir la
   terminal. Si persiste, instala "YubiKey Manager CLI" desde
   https://www.yubico.com/support/download/yubikey-manager/
   y asegurate de que su carpeta este en el PATH de Windows.

4) Conecta la YubiKey.

5) Inicia la aplicacion, con cualquiera de estas dos formas:

   a) Doble clic en iniciar.bat
        - Pedira permisos de Administrador (acepta).
        - Activa los servicios HID y KeyIso, habilita todas las
          interfaces de la llave, abre el navegador y arranca el
          servidor.

   b) Manual (desde una terminal como Administrador):

        python -m uvicorn app:app --host 127.0.0.1 --port 8000

      y luego abre en el navegador:  http://127.0.0.1:8000

6) Para detener la app: cierra la ventana negra o presiona Ctrl + C.


USO DE LA INTERFAZ
------------------
Tarjeta "Eventbrite OTP & Excel":
  1. Espera a que el indicador muestre "Conectada".
  2. Escribe el BMS del agente (ej: 4259379).
  3. Elige el slot (1 = toque corto, 2 = toque largo).
  4. Pulsa "Configurar Llave".
  5. Copia Serial, Private ID y Secret Key con los botones "Copiar".
  6. El boton "Excel" descarga Eventbrite_YubiKeys.xlsx.

Tarjeta "Agente IA":
  1. Pega tu Gemini API Key en el campo superior derecho
     (se guarda en el navegador).
  2. Usa el boton rapido "Limpiar y dejar en FIDO2 (sin PIN)"
     o escribe una instruccion en el chat.

RESET FIDO2 (importante)
  - Debes desconectar y volver a conectar la llave, y tocar el
    sensor dorado dentro de los primeros 5 segundos. Si pasa mas
    tiempo, el reset falla.
  - El reset borra TODO: FIDO2, PIV, OATH, OpenPGP y OTP.


ARCHIVOS QUE GENERA LA APP
--------------------------
  Eventbrite_YubiKeys.xlsx   -> registro acumulado de llaves
  logs_eventbrite\<BMS>.csv  -> un CSV por cada BMS configurado
  (Contienen claves secretas: guardalos de forma segura.)


SOLUCION DE PROBLEMAS
---------------------
  - "Desconectada" aunque la llave esta puesta:
      ejecuta "ykman list" en la terminal; si no la ve, prueba otro
      puerto USB o reconecta la llave.
  - "python no se reconoce": reinstala Python marcando
      "Add Python to PATH".
  - Puerto 8000 ocupado: cambia --port 8000 por otro (ej. 8001) en
      iniciar.bat y abre esa URL.
  - Error de Gemini: revisa que la API Key sea valida y que haya
      conexion a internet.
  - Sin permisos / errores al hablar con la llave: ejecuta la app
      como Administrador.
  - Si un error menciona "pip" no encontrado:
      python -m pip install -r install.txt

==========================================================
