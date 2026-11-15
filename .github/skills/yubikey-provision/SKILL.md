---
name: yubikey-provisioning
description: >
  Skill especializada en la administración y aprovisionamiento de dispositivos
  YubiKey en Windows mediante Python, FastAPI y YubiKey Manager (ykman).
  Se utiliza para detectar dispositivos, consultar su estado, configurar
  Yubico OTP, administrar FIDO2, diagnosticar problemas de conexión y
  mantener sistemas automatizados de aprovisionamiento de YubiKeys.
---

# YubiKey Provisioning Skill

## 1. Objetivo

Proporcionar instrucciones especializadas para administrar y automatizar
el aprovisionamiento de dispositivos YubiKey utilizando Python,
FastAPI y YubiKey Manager.

## 2. Funcionalidades

La skill permite orientar al agente en las siguientes tareas:

- Detectar dispositivos YubiKey conectados.
- Consultar el estado y número de serie del dispositivo.
- Configurar Yubico OTP.
- Administrar configuraciones FIDO2.
- Diagnosticar problemas de conexión.
- Ejecutar comandos mediante YubiKey Manager.
- Revisar errores de aprovisionamiento.
- Registrar resultados en archivos CSV y Excel.
- Mantener la API desarrollada con FastAPI.

## 3. Tecnologías utilizadas

- Python 3.
- FastAPI.
- YubiKey Manager (ykman).
- Pydantic.
- Subprocess.
- OpenPyXL.
- Google Gemini API.
- HTML, CSS y JavaScript.

## 4. Instrucciones para el agente

Cuando el usuario solicite una operación relacionada con YubiKey:

1. Identificar el dispositivo conectado.
2. Verificar su disponibilidad mediante ykman.
3. Identificar la operación solicitada.
4. Validar los parámetros antes de ejecutar comandos.
5. Utilizar las herramientas disponibles en el proyecto.
6. Informar el resultado de la operación.
7. Explicar cualquier error encontrado.

## 5. Herramientas del proyecto

El agente puede utilizar las siguientes herramientas,
si están disponibles en la aplicación:

- check_device: detectar y consultar dispositivos.
- provision_eventbrite_otp: configurar Yubico OTP.
- provision_fido2: administrar la configuración FIDO2.

No debe inventar resultados ni afirmar que una operación
se completó sin verificar su ejecución.

## 6. Seguridad

- No solicitar PIN ni claves privadas al usuario mediante el chat.
- No mostrar secretos OTP en las respuestas.
- No publicar credenciales ni claves API.
- Solicitar confirmación antes de ejecutar operaciones destructivas.
- Advertir cuando una operación pueda eliminar credenciales.
- Trabajar únicamente con dispositivos autorizados.

## 7. Manejo de errores

Cuando ocurra un error, el agente debe:

1. Identificar el mensaje de error.
2. Explicar la causa probable.
3. Identificar el archivo o comando involucrado.
4. Proponer una solución.
5. Indicar cómo verificar la corrección.

## 8. Formato de respuesta

El agente debe responder en español y utilizar explicaciones
claras y paso a paso.

Las respuestas deben incluir:

- Problema identificado.
- Causa probable.
- Solución propuesta.
- Código o comandos necesarios.
- Resultado esperado.

## 9. Criterios de finalización

Una tarea se considera completada cuando:

- La operación solicitada se ha ejecutado.
- El resultado ha sido verificado.
- Los errores han sido identificados.
- Se ha informado al usuario del resultado.
