import os
import traceback

from tkinter import Tk, filedialog

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter
)



# =====================================
# SELECTOR DE CARPETA
# =====================================

def seleccionar_carpeta(titulo):

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    carpeta = filedialog.askdirectory(
        title=titulo
    )

    root.destroy()

    return carpeta



# =====================================
# MEJORADOR XBOX CLASSIC
# =====================================

def mejorar_textura(img):

    img = img.convert("RGBA")


    r,g,b,a = img.split()


    rgb = Image.merge(
        "RGB",
        (r,g,b)
    )


    r,g,b = rgb.split()


    r = r.point(
        lambda x: min(255, int(x * 1.20))
    )


    g = g.point(
        lambda x: min(255, int(x * 1.04))
    )


    b = b.point(
        lambda x: int(x * 0.98)
    )


    rgb = Image.merge(
        "RGB",
        (
            r,
            g,
            b
        )
    )



    rgb = ImageEnhance.Brightness(
        rgb
    ).enhance(1.10)



    rgb = ImageEnhance.Contrast(
        rgb
    ).enhance(1.15)



    rgb = ImageEnhance.Color(
        rgb
    ).enhance(0.94)



    rgb = rgb.filter(
        ImageFilter.UnsharpMask(
            radius=1.0,
            percent=65,
            threshold=4
        )
    )



    suave = rgb.filter(
        ImageFilter.GaussianBlur(0.4)
    )


    rgb = Image.blend(
        rgb,
        suave,
        0.08
    )



    r,g,b = rgb.split()


    resultado = Image.merge(
        "RGBA",
        (
            r,
            g,
            b,
            a
        )
    )


    return resultado
# =====================================
# BUSCAR TEXTURAS RECURSIVAMENTE
# =====================================

def buscar_texturas(carpeta):

    extensiones = [
        ".png",
        ".bmp",
        ".jpg",
        ".jpeg",
        ".tga"
    ]


    archivos = []


    for raiz, carpetas, nombres in os.walk(carpeta):

        for nombre in nombres:

            extension = os.path.splitext(nombre)[1].lower()


            if extension in extensiones:

                ruta = os.path.join(
                    raiz,
                    nombre
                )

                archivos.append(
                    ruta
                )


    return archivos



# =====================================
# CREAR RUTA DE SALIDA
# MANTIENE SUBCARPETAS
# =====================================

def crear_destino(ruta_original, entrada, salida):

    relativa = os.path.relpath(
        ruta_original,
        entrada
    )


    destino = os.path.join(
        salida,
        relativa
    )


    carpeta = os.path.dirname(
        destino
    )


    os.makedirs(
        carpeta,
        exist_ok=True
    )


    return destino
# =====================================
# PROGRAMA PRINCIPAL
# =====================================

def main():

    print("==============================")
    print(" XBOX CLASSIC TEXTURE ENHANCER")
    print(" MODO MASIVO RECURSIVO")
    print("==============================")
    print()



    entrada = seleccionar_carpeta(
        "Selecciona carpeta con texturas"
    )


    if not entrada:

        print("Cancelado")
        input()
        return



    salida = seleccionar_carpeta(
        "Selecciona carpeta de salida"
    )


    if not salida:

        print("Cancelado")
        input()
        return



    archivos = buscar_texturas(
        entrada
    )



    if not archivos:

        print("No se encontraron texturas")
        input()
        return



    print()
    print(
        "Texturas encontradas:",
        len(archivos)
    )
    print()



    correctas = 0
    errores = 0



    for i,ruta in enumerate(archivos,1):

        try:

            nombre = os.path.basename(
                ruta
            )


            print(
                f"[{i}/{len(archivos)}] {nombre}"
            )



            destino = crear_destino(
                ruta,
                entrada,
                salida
            )



            img = Image.open(
                ruta
            )



            resultado = mejorar_textura(
                img
            )



            resultado.save(
                destino
            )


            correctas += 1



        except Exception:

            errores += 1

            print(
                "ERROR:",
                ruta
            )

            traceback.print_exc()



    print()
    print("==============================")
    print(" TERMINADO")
    print("==============================")
    print(
        "Procesadas:",
        correctas
    )
    print(
        "Errores:",
        errores
    )


    input("\nENTER para cerrar")



if __name__=="__main__":

    main()