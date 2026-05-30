import socket
import subprocess
import os
import glob
from datetime import datetime

HOST = '0.0.0.0'
PORT = 9100

print("=" * 60)
print("🟢 SERVIDOR ATS ACTIVO - MODO LECTURA VISUAL (OCR)")
print("-> Esperando impresión... Generando texto editable.")
print("=" * 60)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    
    while True:
        try:
            conn, addr = s.accept()
            with conn:
                print(f"\n[+] Impresión detectada desde el ATS ({addr[0]})")
                datos_completos = b""
                
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    datos_completos += data
                
                if datos_completos:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archivo_final_txt = f"Alarmas_Editables_{timestamp}.txt"
                    temp_ps = "temp_crudo.ps"
                    
                    print("⏳ Paso 1/3: Recibiendo reporte...")
                    with open(temp_ps, "wb") as f:
                        f.write(datos_completos)
                        
                    print("⏳ Paso 2/3: Renderizando imagen de alta resolución...")
                    # Ghostscript convierte el código en una imagen PNG clara
                    gs_cmd = [
                        "gs", "-q", "-dNOPAUSE", "-dBATCH", 
                        "-sDEVICE=png16m", "-r300", 
                        "-sOutputFile=temp_pagina_%02d.png", 
                        temp_ps
                    ]
                    subprocess.run(gs_cmd, check=True)
                    
                    print("⏳ Paso 3/3: Extrayendo texto con Inteligencia Artificial...")
                    texto_total = ""
                    
                    # Buscar todas las páginas que se hayan generado
                    paginas_png = sorted(glob.glob("temp_pagina_*.png"))
                    
                    for png in paginas_png:
                        # Tesseract lee la imagen en español y extrae el texto
                        tesseract_cmd = ["tesseract", png, "temp_ocr", "-l", "spa"]
                        subprocess.run(tesseract_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        # Guardar el texto extraído
                        with open("temp_ocr.txt", "r", encoding="utf-8") as f:
                            texto_total += f.read() + "\n"
                            
                        # Borrar la imagen temporal
                        os.remove(png)
                        
                    # Crear tu archivo final limpio y editable
                    with open(archivo_final_txt, "w", encoding="utf-8") as f:
                        f.write(texto_total)
                        
                    # Limpiar la basura
                    if os.path.exists(temp_ps): os.remove(temp_ps)
                    if os.path.exists("temp_ocr.txt"): os.remove("temp_ocr.txt")
                    
                    print(f"✅ ¡ÉXITO TOTAL! Reporte convertido a texto.")
                    print(f"📄 Archivo listo para editar: {archivo_final_txt}")
                    print("-" * 60)
                    
        except KeyboardInterrupt:
            print("\nServidor detenido. ¡Buen turno!")
            break
        except Exception as e:
            print(f"\n[!] Error procesando el documento: {e}")