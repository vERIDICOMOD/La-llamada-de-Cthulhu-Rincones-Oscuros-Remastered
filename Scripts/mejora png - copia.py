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


    # -------------------------------
    # COLOR XBOX
    # Rojo y verde más fuertes
    # Azul reducido
    # -------------------------------

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



    # -------------------------------
    # LUZ
    # -------------------------------

    rgb = ImageEnhance.Brightness(
        rgb
    ).enhance(1.10)



    # -------------------------------
    # SOMBRAS MARCADAS
    # -------------------------------

    rgb = ImageEnhance.Contrast(
        rgb
    ).enhance(1.15)



    # -------------------------------
    # SATURACION
    # -------------------------------

    rgb = ImageEnhance.Color(
        rgb
    ).enhance(0.94)



    # -------------------------------
    # CLARIDAD / NITIDEZ
    # -------------------------------

    rgb = rgb.filter(
        ImageFilter.UnsharpMask(
        	radius=1.0,
        	percent=65,
      		threshold=4
        )
    )



    # -------------------------------
    # REDUCCION SUAVE DE RUIDO DXT
    # -------------------------------

    suave = rgb.filter(
        ImageFilter.GaussianBlur(0.4)
    )


    rgb = Image.blend(
        rgb,
        suave,
        0.08
    )



    # -------------------------------
    # RESTAURAR ALFA ORIGINAL
    # -------------------------------

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
# PROGRAMA PRINCIPAL
# =====================================

def main():

    print("==============================")
    print(" XBOX CLASSIC TEXTURE ENHANCER")
    print("==============================")
    print()


    entrada = seleccionar_carpeta(
        "Selecciona carpeta de texturas"
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



    formatos=[
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tga"
    ]


    archivos=[]


    for f in os.listdir(entrada):

        if os.path.splitext(f)[1].lower() in formatos:
            archivos.append(f)



    print(
        "Texturas:",
        len(archivos)
    )



    for i,f in enumerate(archivos):

        try:

            print(
                f"[{i+1}/{len(archivos)}]",
                f
            )


            ruta=os.path.join(
                entrada,
                f
            )


            destino=os.path.join(
                salida,
                f
            )


            img=Image.open(
                ruta
            )


            resultado=mejorar_textura(
                img
            )


            resultado.save(
                destino
            )


        except Exception:

            print(
                "ERROR:",
                f
            )

            traceback.print_exc()



    print()
    print("==============================")
    print(" TERMINADO")
    print("==============================")


    input("ENTER para cerrar")



if __name__=="__main__":
    main()
# =====================================
# PROCESAR CARPETA
# =====================================

def main():

    print("==============================")
    print(" XBOX CLASSIC TEXTURE ENHANCER")
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



    extensiones=[
        ".png",
        ".bmp",
        ".jpg",
        ".jpeg",
        ".tga"
    ]



    archivos=[]


    for f in os.listdir(entrada):

        if os.path.splitext(f)[1].lower() in extensiones:
            archivos.append(f)



    print(
        "Texturas encontradas:",
        len(archivos)
    )



    for i,f in enumerate(archivos):

        try:

            print(
                f"[{i+1}/{len(archivos)}]",
                f
            )


            ruta=os.path.join(
                entrada,
                f
            )


            destino=os.path.join(
                salida,
                f
            )


            img=Image.open(
                ruta
            )


            resultado=mejorar_textura(
                img
            )


            resultado.save(
                destino
            )


        except Exception:

            print(
                "ERROR:",
                f
            )

            traceback.print_exc()



    print()
    print("==============================")
    print(" TERMINADO")
    print("==============================")


    input("ENTER para cerrar")



if __name__=="__main__":
    main()