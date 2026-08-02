# ============================================================
# XPR Injector Masivo
# PARTE 1/4
# Lectura XPR + estructuras
# ============================================================

import os
import json
import struct
import traceback

from tkinter import Tk, filedialog
from PIL import Image



# ============================================================
# EndianStream
# ============================================================

class EndianStream:

    def __init__(self, data, order="little"):

        self.data = data
        self.position = 0
        self.order = order


    def seek(self, pos):

        self.position = pos


    def tell(self):

        return self.position


    def read_bytes(self, count):

        end = self.position + count

        if end > len(self.data):

            raise EOFError(
                "Lectura fuera del archivo"
            )

        result = self.data[
            self.position:end
        ]

        self.position = end

        return result


    def read_uint8(self):

        return self.read_bytes(1)[0]


    def read_uint16(self):

        return int.from_bytes(
            self.read_bytes(2),
            self.order
        )


    def read_uint32(self):

        return int.from_bytes(
            self.read_bytes(4),
            self.order
        )


    def write_bytes(self, data):

        end = self.position + len(data)

        if end > len(self.data):

            self.data.extend(
                b"\x00" *
                (end-len(self.data))
            )


        self.data[
            self.position:end
        ] = data


        self.position = end




# ============================================================
# Tipos XPR
# ============================================================

class XprResourceType:

    Texture = 4




class XprTexture:

    def __init__(self, data):

        self.id = data["id"]
        self.file = data["file"]
        self.offset = data["offset"]
        self.size = data["size"]
        self.width = data["width"]
        self.height = data["height"]
        self.format = data["format"]




def load_texture_database(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)


    return [
        XprTexture(x)
        for x in data
    ]




# ============================================================
# Recursos XPR
# ============================================================

class XprResource:

    def __init__(self):

        self.id = 0
        self.type = 0
        self.common = 0
        self.data_offset = 0
        self.gpu_format = 0




# ============================================================
# Lector XPR
# ============================================================

class XprFile:


    def __init__(self, path):

        self.path = path


        with open(
            path,
            "rb"
        ) as f:

            self.data = bytearray(
                f.read()
            )


        self.stream = EndianStream(
            self.data
        )


        self.header_size = 0
        self.resources = []




    def read_header(self):

        self.stream.seek(0)


        magic = self.stream.read_bytes(4)


        if magic != b"XPR0":

            raise Exception(
                "Archivo no es XPR0"
            )


        self.stream.seek(8)


        self.header_size = (
            self.stream.read_uint32()
        )




    def read_resources(self):

        self.resources.clear()


        pos = 12
        index = 0


        while pos < self.header_size:


            if pos + 20 > len(self.data):

                break


            self.stream.seek(pos)


            res = XprResource()


            res.id = index


            res.common = (
                self.stream.read_uint32()
            )


            res.data_offset = (
                self.stream.read_uint32()
            )


            self.stream.seek(
                pos + 12
            )


            res.gpu_format = (
                self.stream.read_uint32()
            )


            res.type = (
                (res.common >> 16)
                & 7
            )


            self.resources.append(
                res
            )


            pos += 20
            index += 1
# ============================================================
# PARTE 2/4
# Encoder DXT1 / DXT5
# ============================================================


def rgb_to_565(r,g,b):

    return (
        ((r >> 3) << 11)
        |
        ((g >> 2) << 5)
        |
        (b >> 3)
    )



def color_565_to_rgb(c):

    r = (
        ((c >> 11) & 31)
        * 255
        //
        31
    )

    g = (
        ((c >> 5) & 63)
        * 255
        //
        63
    )

    b = (
        c & 31
    ) * 255 // 31


    return r,g,b




# ============================================================
# DXT1
# ============================================================

def encode_dxt1(img):

    width,height = img.size

    pixels = img.convert(
        "RGBA"
    ).load()


    output = bytearray()


    for by in range(0,height,4):

        for bx in range(0,width,4):

            block=[]


            for y in range(4):

                for x in range(4):

                    px=min(
                        bx+x,
                        width-1
                    )

                    py=min(
                        by+y,
                        height-1
                    )


                    block.append(
                        pixels[px,py]
                    )



            cmax=max(
                block,
                key=lambda c:
                c[0]+c[1]+c[2]
            )


            cmin=min(
                block,
                key=lambda c:
                c[0]+c[1]+c[2]
            )


            c0=rgb_to_565(
                cmax[0],
                cmax[1],
                cmax[2]
            )


            c1=rgb_to_565(
                cmin[0],
                cmin[1],
                cmin[2]
            )


            if c0 < c1:

                c0,c1=c1,c0



            colors=[

                color_565_to_rgb(c0),

                color_565_to_rgb(c1)

            ]


            colors.append(
                (
                    (2*colors[0][0]+colors[1][0])//3,
                    (2*colors[0][1]+colors[1][1])//3,
                    (2*colors[0][2]+colors[1][2])//3
                )
            )


            colors.append(
                (
                    (colors[0][0]+2*colors[1][0])//3,
                    (colors[0][1]+2*colors[1][1])//3,
                    (colors[0][2]+2*colors[1][2])//3
                )
            )



            bits=0


            for i,p in enumerate(block):

                best=0
                dist=999999999


                for n,c in enumerate(colors):

                    d=(

                        (p[0]-c[0])**2
                        +
                        (p[1]-c[1])**2
                        +
                        (p[2]-c[2])**2

                    )


                    if d < dist:

                        dist=d
                        best=n



                bits |= (
                    best <<
                    (i*2)
                )



            output += struct.pack(
                "<HHI",
                c0,
                c1,
                bits
            )


    return bytes(output)





# ============================================================
# DXT5 Alpha
# ============================================================

def encode_alpha_block(values):

    a0=max(values)
    a1=min(values)


    table=[a0,a1]


    table += [

        (6*a0+a1)//7,
        (5*a0+2*a1)//7,
        (4*a0+3*a1)//7,
        (3*a0+4*a1)//7,
        (2*a0+5*a1)//7,
        (a0+6*a1)//7

    ]


    bits=0


    for i,a in enumerate(values):

        best=min(
            range(8),
            key=lambda x:
            abs(
                a-table[x]
            )
        )


        bits |= (
            best <<
            (i*3)
        )


    return (
        bytes([a0,a1])
        +
        bits.to_bytes(
            6,
            "little"
        )
    )
# ============================================================
# PARTE 3/4
# Bloques DXT5 + Inyector XPR
# ============================================================


def encode_color_block(colors):


    cmax=max(
        colors,
        key=lambda c:
        c[0]+c[1]+c[2]
    )


    cmin=min(
        colors,
        key=lambda c:
        c[0]+c[1]+c[2]
    )


    c0=rgb_to_565(
        cmax[0],
        cmax[1],
        cmax[2]
    )


    c1=rgb_to_565(
        cmin[0],
        cmin[1],
        cmin[2]
    )


    if c0 < c1:

        c0,c1=c1,c0



    palette=[

        color_565_to_rgb(c0),

        color_565_to_rgb(c1)

    ]


    palette += [

        (
        (2*palette[0][0]+palette[1][0])//3,
        (2*palette[0][1]+palette[1][1])//3,
        (2*palette[0][2]+palette[1][2])//3
        ),

        (
        (palette[0][0]+2*palette[1][0])//3,
        (palette[0][1]+2*palette[1][1])//3,
        (palette[0][2]+2*palette[1][2])//3
        )

    ]


    bits=0


    for i,p in enumerate(colors):

        index=min(
            range(4),
            key=lambda n:
            (
                (p[0]-palette[n][0])**2
                +
                (p[1]-palette[n][1])**2
                +
                (p[2]-palette[n][2])**2
            )
        )


        bits |= (
            index <<
            (i*2)
        )


    return struct.pack(
        "<HHI",
        c0,
        c1,
        bits
    )





def encode_dxt5(img):

    width,height=img.size

    pixels=img.convert(
        "RGBA"
    ).load()


    output=bytearray()


    for by in range(0,height,4):

        for bx in range(0,width,4):

            block=[]


            for y in range(4):

                for x in range(4):

                    px=min(
                        bx+x,
                        width-1
                    )

                    py=min(
                        by+y,
                        height-1
                    )


                    block.append(
                        pixels[px,py]
                    )


            output += encode_alpha_block(
                [
                    p[3]
                    for p in block
                ]
            )


            output += encode_color_block(
                block
            )


    return bytes(output)





# ============================================================
# Inyector XPR
# ============================================================


class XprInjector:


    def __init__(self,path):


        with open(
            path,
            "rb"
        ) as f:

            self.data=bytearray(
                f.read()
            )


        self.xpr=XprFile(
            path
        )


        self.xpr.data=self.data


        self.xpr.stream=EndianStream(
            self.data
        )


        self.xpr.read_header()

        self.xpr.read_resources()




    def find_texture(self, tex_id):


        for res in self.xpr.resources:


            if res.id == tex_id:

                gpu=res.gpu_format


                fmt=(gpu >> 8) & 0xff


                if fmt == 0x0C:

                    name="DXT1"

                elif fmt == 0x0F:

                    name="DXT5"

                else:

                    continue



                return {

                    "id":tex_id,

                    "offset":
                    self.xpr.header_size
                    +
                    res.data_offset,

                    "format":name

                }



        return None




    def write_texture(
            self,
            offset,
            data
    ):


        end=offset+len(data)


        if end > len(self.data):

            raise Exception(
                "Datos fuera del XPR"
            )


        self.data[
            offset:end
        ]=data
# ============================================================
# PARTE 4/4
# INYECCION MASIVA + MAIN
# ============================================================



def convertir_textura(
        png_path,
        formato
):


    img=Image.open(
        png_path
    )


    img=img.convert(
        "RGBA"
    )


    if formato=="DXT1":

        return encode_dxt1(
            img
        )


    elif formato=="DXT5":

        return encode_dxt5(
            img
        )


    else:

        raise Exception(
            "Formato desconocido: "
            +
            str(formato)
        )





def inyectar_xpr(
        xpr_path,
        json_path,
        carpeta_png,
        salida
):


    print()
    print("----------------------------")
    print(
        "INYECTANDO:",
        xpr_path
    )
    print("----------------------------")


    injector=XprInjector(
        xpr_path
    )


    textures=load_texture_database(
        json_path
    )


    correctas=0



    for tex in textures:


        try:

            png=os.path.join(
                carpeta_png,
                tex.file
            )


            if not os.path.isfile(png):

                print(
                    "Falta:",
                    tex.file
                )

                continue



            data=convertir_textura(
                png,
                tex.format
            )



            if len(data)!=tex.size:

                raise Exception(
                    "Tamaño diferente "
                    +
                    str(len(data))
                    +
                    "/"
                    +
                    str(tex.size)
                )



            info=injector.find_texture(
                tex.id
            )


            if info is None:

                raise Exception(
                    "Textura no encontrada"
                )



            injector.write_texture(
                info["offset"],
                data
            )


            correctas+=1


            print(
                "OK:",
                tex.file
            )



        except Exception as e:


            print(
                "ERROR:",
                tex.file,
                e
            )



    with open(
        salida,
        "wb"
    ) as f:

        f.write(
            injector.data
        )



    print(
        "TEXTURAS INSERTADAS:",
        correctas
    )





# ============================================================
# BUSQUEDA DE CARPETAS
# ============================================================


def buscar_archivo(
        carpeta,
        nombre
):


    for raiz,dirs,files in os.walk(carpeta):


        if nombre in files:

            return os.path.join(
                raiz,
                nombre
            )


    return None




def procesar_masivo(
        original,
        modificadas,
        resultado
):


    for raiz,dirs,files in os.walk(modificadas):


        if "textures.json" not in files:

            continue



        carpeta_actual=raiz



        relativa=os.path.relpath(
            carpeta_actual,
            modificadas
        )


        carpeta_original=os.path.join(
            original,
            relativa
        )


        xpr=os.path.join(
            carpeta_original,
            "Textures.xpr"
        )


        if not os.path.isfile(xpr):

            print(
                "No existe:",
                xpr
            )

            continue



        salida_carpeta=os.path.join(
            resultado,
            relativa
        )


        os.makedirs(
            salida_carpeta,
            exist_ok=True
        )


        salida=os.path.join(
            salida_carpeta,
            "Textures_NEW.xpr"
        )



        json_file=os.path.join(
            carpeta_actual,
            "textures.json"
        )



        inyectar_xpr(
            xpr,
            json_file,
            carpeta_actual,
            salida
        )






# ============================================================
# MAIN
# ============================================================


def main():


    try:


        root=Tk()

        root.withdraw()



        original=filedialog.askdirectory(
            title="Selecciona carpeta padre ORIGINAL"
        )


        if not original:

            return



        modificadas=filedialog.askdirectory(
            title="Selecciona carpeta padre PNG modificadas"
        )


        if not modificadas:

            return



        resultado=filedialog.askdirectory(
            title="Selecciona carpeta RESULTADO"
        )


        if not resultado:

            return



        procesar_masivo(
            original,
            modificadas,
            resultado
        )



        print()
        print("======================")
        print(" TERMINADO")
        print("======================")



    except Exception:


        traceback.print_exc()



    input(
        "\nENTER para cerrar..."
    )





if __name__=="__main__":

    main()