import struct
import os
import json
import traceback

try:
    from tkinter import Tk, filedialog
except Exception as e:
    print("Error cargando Tkinter:")
    print(e)
    input("ENTER para salir")
    raise

try:
    from PIL import Image
except Exception as e:
    print("Falta Pillow:")
    print(e)
    input("ENTER para salir")
    raise



def read_u32(data, pos):
    return struct.unpack_from("<I", data, pos)[0]



def rgb565(c):
    r = ((c >> 11) & 31) * 255 // 31
    g = ((c >> 5) & 63) * 255 // 63
    b = (c & 31) * 255 // 31
    return r,g,b



# -------------------------------------------------
# DXT1
# -------------------------------------------------

def decode_dxt1(data,width,height):

    img=Image.new("RGBA",(width,height))
    pix=img.load()

    offset=0

    for by in range((height+3)//4):
        for bx in range((width+3)//4):

            c0,c1,bits=struct.unpack_from("<HHI",data,offset)
            offset+=8

            r0,g0,b0=rgb565(c0)
            r1,g1,b1=rgb565(c1)

            colors=[
                (r0,g0,b0,255),
                (r1,g1,b1,255)
            ]

            if c0>c1:
                colors.append(
                    (
                    (2*r0+r1)//3,
                    (2*g0+g1)//3,
                    (2*b0+b1)//3,
                    255
                    ))

                colors.append(
                    (
                    (r0+2*r1)//3,
                    (g0+2*g1)//3,
                    (b0+2*b1)//3,
                    255
                    ))

            else:
                colors.append(
                    (
                    (r0+r1)//2,
                    (g0+g1)//2,
                    (b0+b1)//2,
                    255
                    ))

                colors.append((0,0,0,0))


            for y in range(4):
                for x in range(4):

                    index=bits & 3
                    bits >>= 2

                    px=bx*4+x
                    py=by*4+y

                    if px<width and py<height:
                        pix[px,py]=colors[index]


    return img



# -------------------------------------------------
# DXT5
# -------------------------------------------------

def decode_dxt5(data,width,height):

    img=Image.new("RGBA",(width,height))
    pix=img.load()

    offset=0


    for by in range((height+3)//4):
        for bx in range((width+3)//4):

            a0=data[offset]
            a1=data[offset+1]

            abits=int.from_bytes(
                data[offset+2:offset+8],
                "little"
            )

            offset+=8


            alpha=[a0,a1]

            if a0>a1:
                alpha += [
                    (6*a0+a1)//7,
                    (5*a0+2*a1)//7,
                    (4*a0+3*a1)//7,
                    (3*a0+4*a1)//7,
                    (2*a0+5*a1)//7,
                    (a0+6*a1)//7
                ]

            else:
                alpha += [
                    (4*a0+a1)//5,
                    (3*a0+2*a1)//5,
                    (2*a0+3*a1)//5,
                    (a0+4*a1)//5,
                    0,
                    255
                ]


            c0,c1,bits=struct.unpack_from(
                "<HHI",
                data,
                offset
            )

            offset+=8


            r0,g0,b0=rgb565(c0)
            r1,g1,b1=rgb565(c1)


            colors=[
                (r0,g0,b0),
                (r1,g1,b1),
                (
                (2*r0+r1)//3,
                (2*g0+g1)//3,
                (2*b0+b1)//3
                ),
                (
                (r0+2*r1)//3,
                (g0+2*g1)//3,
                (b0+2*b1)//3
                )
            ]


            for y in range(4):
                for x in range(4):

                    ci=bits&3
                    bits>>=2

                    ai=abits&7
                    abits>>=3


                    px=bx*4+x
                    py=by*4+y


                    if px<width and py<height:

                        r,g,b=colors[ci]

                        pix[px,py]=(
                            r,
                            g,
                            b,
                            alpha[ai]
                        )

    return img




# -------------------------------------------------
# XPR
# -------------------------------------------------

def extract_xpr(path,outdir):

    with open(path,"rb") as f:
        data=f.read()


    if data[:4]!=b"XPR0":
        raise Exception("El archivo no es XPR0")


    header=read_u32(data,8)


    textures=[]

    pos=12
    index=0


    while pos<header:

        if pos+20>len(data):
            break


        common=read_u32(data,pos)
        data_offset=read_u32(data,pos+4)
        gpu=read_u32(data,pos+12)


        rtype=(common>>16)&7


        if rtype==4:

            fmt=(gpu>>8)&0xff


            width=1<<((gpu>>20)&15)
            height=1<<((gpu>>24)&15)


            texpos=header+data_offset


            if fmt==0x0c:

                namefmt="DXT1"
                size=(width*height)//2
                decoder=decode_dxt1


            elif fmt==0x0f:

                namefmt="DXT5"
                blocks=((width+3)//4)*((height+3)//4)
                size=blocks*16
                decoder=decode_dxt5


            else:
                pos+=20
                index+=1
                continue


            if texpos+size>len(data):
                pos+=20
                index+=1
                continue


            tex=data[texpos:texpos+size]


            img=decoder(
                tex,
                width,
                height
            )


            filename=f"texture_{index:03}_{namefmt}_{width}x{height}.png"


            img.save(
                os.path.join(outdir,filename)
            )


            textures.append({
                "id":index,
                "file":filename,
                "offset":texpos,
                "size":size,
                "width":width,
                "height":height,
                "format":namefmt
            })


        pos+=20
        index+=1



    with open(
        os.path.join(outdir,"textures.json"),
        "w"
    ) as f:
        json.dump(
            textures,
            f,
            indent=4
        )


    print("Texturas:",len(textures))




# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():

    try:

        Tk().withdraw()


        archivo=filedialog.askopenfilename(
            title="Selecciona XPR",
            filetypes=[
                ("Xbox Resource","*.xpr"),
                ("Todos","*.*")
            ]
        )


        if not archivo:
            return


        salida=filedialog.askdirectory(
            title="Carpeta salida"
        )


        if not salida:
            return


        extract_xpr(
            archivo,
            salida
        )


        print("\nLISTO")


    except Exception:

        traceback.print_exc()


    input("\nENTER para cerrar")



if __name__=="__main__":
    main()