import os
import tkinter as tk
from tkinter import filedialog

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde buscar")
    return carpeta

def renombrar_xpr(carpeta_raiz):
    contador = 0

    for ruta_actual, carpetas, archivos in os.walk(carpeta_raiz):
        for archivo in archivos:
            if archivo.lower().endswith(".xpr"):
                ruta_vieja = os.path.join(ruta_actual, archivo)
                ruta_nueva = os.path.join(ruta_actual, "Textures.xpr")

                # Si ya existe un Textures.xpr, no lo reemplaza
                if os.path.exists(ruta_nueva):
                    print(f"Omitido (ya existe): {ruta_nueva}")
                    continue

                os.rename(ruta_vieja, ruta_nueva)
                contador += 1
                print(f"Renombrado: {ruta_vieja} -> {ruta_nueva}")

    return contador


# Crear ventana oculta
root = tk.Tk()
root.withdraw()

# Seleccionar carpeta
carpeta = seleccionar_carpeta()

if carpeta:
    cantidad = renombrar_xpr(carpeta)
    print(f"\nProceso terminado. Archivos renombrados: {cantidad}")
else:
    print("No se seleccionó ninguna carpeta.")