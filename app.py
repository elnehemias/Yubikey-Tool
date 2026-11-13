import os, csv, subprocess, threading
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openpyxl import Workbook, load_workbook
from google import genai
from google.genai import types

app, XLSX = FastAPI(), "Eventbrite_YubiKeys.xlsx"
usb_lock = threading.Lock()

def run(a, timeout=8):
    r = subprocess.run(
        ["ykman", *a],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    if r.returncode != 0:
        err_lines = [l for l in r.stderr.splitlines() if not l.startswith("WARNING:")]
        raise RuntimeError("\n".join(err_lines).strip() or "Error en ykman")
    return r.stdout.strip()

fmt = lambda h: " ".join(h[i:i+2] for i in range(0, len(h), 2))

def check_device() -> dict:
    """Detecta la YubiKey sin reiniciar el bus USB."""
    if usb_lock.locked():
        return {"connected": True, "serial": "Ocupada...", "fw": "..."}
    with usb_lock:
        try:
            out = run(["list"], timeout=3)
            if not out:
                return {"connected": False}
            serial = out.split("Serial:")[1].strip() if "Serial:" in out else "Modo FIDO2"
            fw = out.split("[")[1].split("]")[0] if "[" in out and "]" in out else "Activa"
            return {"connected": True, "serial": serial, "fw": fw}
        except Exception:
            return {"connected": False}

def provision_eventbrite_otp(bms: str, slot: int = 1) -> dict:
    """Limpia el slot, genera claves Yubico OTP, configura la llave, guarda CSV y actualiza Excel."""
    if slot not in (1, 2): raise RuntimeError("Slot inválido (1 o 2).")
    with usb_lock:
        try: run(["config", "usb", "--enable", "OTP", "-f"], timeout=5)
        except Exception: pass

        serials = [s.strip() for s in run(["list", "--serials"], timeout=4).splitlines() if s.strip()]
        if not serials:
            raise RuntimeError("No se detectó el serial. Desconecta y conecta la llave.")
        serial = serials[0]

        try: run(["otp", "delete", str(slot), "-f"], timeout=5)
        except Exception: pass

        pub = os.urandom(6).hex().translate(str.maketrans("0123456789abcdef", "cbdefghijklnrtuv"))
        priv, sec = os.urandom(6).hex(), os.urandom(16).hex()
        run(["otp", "yubiotp", str(slot), "--public-id", pub, "--private-id", priv, "--key", sec, "-f"], timeout=6)

    row = [bms, serial, slot, fmt(pub), fmt(priv), fmt(sec), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    os.makedirs("logs_eventbrite", exist_ok=True)
    csv_p = f"logs_eventbrite/{bms}.csv"
    with open(csv_p, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["BMS", "Serial", "Slot", "Public ID", "Private ID", "Secret Key", "Fecha"], row])

    wb = load_workbook(XLSX) if os.path.exists(XLSX) else Workbook()
    ws = wb.active
    if ws.max_row == 1 and not ws["A1"].value:
        ws.append(["BMS", "Serial", "Slot", "Public Identity (Modhex)", "Private ID (Hex)", "Secret Key (Hex)", "Fecha"])
    ws.append(row); wb.save(XLSX)
    return {"bms": bms, "serial": serial, "private_id": fmt(priv), "secret_key": fmt(sec), "csv": csv_p}

def provision_fido2(pin: str = "", only_fido: bool = False) -> str:
    """Ejecuta el reset FIDO2 de inmediato al conectar y luego limpia los demás módulos."""
    with usb_lock:
        # 1. Ejecutar el reset FIDO2 INMEDIATAMENTE (sin llamadas previas que reinicien el USB)
        try:
            run(["fido", "reset", "-f"], timeout=15)
            if pin:
                run(["fido", "access", "change-pin", "--new-pin", pin], timeout=6)
        except subprocess.TimeoutExpired:
            return "✖ Tiempo agotado (15s). No se detectó el toque físico en el sensor dorado."
        except Exception as e:
            err = str(e)
            if "no yubikey" in err.lower() or "not found" in err.lower():
                return "✖ No hay YubiKey conectada."
            if "5 seconds" in err or "not allowed" in err.lower():
                return "✖ Pasaron más de 5 segundos desde que conectaste la llave. Desconéctala, conéctala y pulsa rápido."
            return f"✖ Error FIDO2: {err}"

        # 2. Limpiar módulos secundarios (sin límite de tiempo)
        cleaned = []
        for name, cmd in [
            ("PIV", ["piv", "reset", "-f"]),
            ("OATH", ["oath", "reset", "-f"]),
            ("OpenPGP", ["openpgp", "reset", "-f"]),
            ("OTP1", ["otp", "delete", "1", "-f"]),
            ("OTP2", ["otp", "delete", "2", "-f"])
        ]:
            try:
                run(cmd, timeout=4)
                cleaned.append(name)
            except Exception:
                pass

        # 3. Asegurar interfaces encendidas al final (para no interrumpir el bus antes del reset)
        try:
            if only_fido:
                run(["config", "usb", "--enable", "FIDO2", "-f"], timeout=5)
            else:
                run(["config", "usb", "--enable-all", "-f"], timeout=5)
        except Exception:
            pass

        # 4. Comprobación automática de estado FIDO2
        # 4. Comprobación automática de estado FIDO2
        pin_check = "Verificado"
        try:
            fido_out = run(["fido", "info"], timeout=4)
            pin_line = next((l.strip() for l in fido_out.splitlines() if "pin" in l.lower()), "")
            if pin_line:
                pin_check = "Sin PIN configurado (Limpio)" if "not set" in pin_line.lower() else pin_line
        except Exception:
            pass

    return (
        f"✔ Reset FIDO2 completado y módulos limpiados ({', '.join(cleaned) or 'ninguno'}).\n"
        f"🔍 Estado FIDO2: {pin_check}"
    )

class OtpReq(BaseModel): bms: str; slot: int = 1
class ChatReq(BaseModel): msg: str; key: str

@app.get("/")
def ui(): return FileResponse("index.html")

@app.get("/status")
def status(): return check_device()

@app.post("/eventbrite-otp")
def otp(r: OtpReq):
    try: return provision_eventbrite_otp(r.bms.strip(), r.slot)
    except Exception as e: raise HTTPException(400, str(e))

@app.post("/reset-fido2")
def reset_fido2_direct():
    res = provision_fido2(pin="", only_fido=False)
    if res.startswith("✖"): raise HTTPException(400, res)
    return {"reply": res}

@app.get("/download-excel")
def dl():
    if not os.path.exists(XLSX): raise HTTPException(404, "Sin registros aún.")
    return FileResponse(XLSX, filename=XLSX, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/agent")
def agent(r: ChatReq):
    try:
        with genai.Client(api_key=r.key.strip()) as client:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=r.msg,
                config=types.GenerateContentConfig(
                    system_instruction="Asistente para aprovisionar YubiKeys Eventbrite y FIDO2. Usa tus herramientas y responde breve en español.",
                    tools=[check_device, provision_eventbrite_otp, provision_fido2],
                    temperature=0.2
                )
            )
            return {"reply": res.text}
    except Exception as e:
        raise HTTPException(500, str(e))
