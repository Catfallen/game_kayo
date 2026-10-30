"""Desenha as tiras de caminhada dos bichos (bode e galinha do sertao, capivara da Lagoa Maior),
de perfil para a direita.

Saida: assets/bichos/<bicho>.png, 8 quadros de 96x96 lado a lado. O tools/gerar_sprites.py
reduz cada tira para o tamanho do jogo (STRIPS), poe contorno e exporta para o template.
Deterministico. Uso:  python -I tools/gerar_bichos.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

F = 96
N = 8


def bode(i):
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = math.sin(2 * math.pi * i / N)
    bob = 1 if abs(s) > 0.7 else 0
    pelo, sombra, mancha = (232, 226, 212, 255), (180, 170, 152, 255), (150, 104, 62, 255)
    casco, chifre = (60, 46, 36, 255), (110, 100, 92, 255)
    # pernas: pares diagonais se movem juntos
    for x, sign in ((30, 1), (38, -1), (60, -1), (68, 1)):
        dx = round(sign * s * 6)
        d.line((x, 58 + bob, x + dx, 82), fill=sombra if sign < 0 else pelo, width=5)
        d.rectangle((x + dx - 2, 80, x + dx + 3, 84), fill=casco)
    d.ellipse((20, 36 + bob, 76, 66 + bob), fill=pelo)
    d.ellipse((24, 56 + bob, 72, 66 + bob), fill=sombra)
    d.ellipse((34, 40 + bob, 50, 52 + bob), fill=mancha)
    d.polygon(((20, 44 + bob), (12, 34 + bob), (18, 42 + bob)), fill=pelo)  # rabo
    d.polygon(((62, 44 + bob), (70, 24 + bob), (80, 26 + bob), (72, 48 + bob)), fill=pelo)  # pescoco
    d.ellipse((66, 18 + bob, 86, 36 + bob), fill=pelo)  # cabeca
    d.ellipse((78, 26 + bob, 92, 38 + bob), fill=pelo)  # focinho
    d.arc((56, 8 + bob, 78, 30 + bob), 200, 320, fill=chifre, width=4)  # chifre
    d.polygon(((68, 24 + bob), (58, 30 + bob), (66, 30 + bob)), fill=sombra)  # orelha
    d.polygon(((82, 36 + bob), (86, 48 + bob), (88, 36 + bob)), fill=sombra)  # barbicha
    d.ellipse((79, 23 + bob, 82, 26 + bob), fill=(20, 16, 12, 255))  # olho
    return im


def galinha(i):
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = math.sin(2 * math.pi * i / N)
    bob = 2 if abs(s) > 0.7 else 0
    pena, sombra = (238, 232, 220, 255), (196, 186, 170, 255)
    crista, bico = (210, 40, 40, 255), (240, 190, 60, 255)
    for x, sign in ((44, 1), (52, -1)):
        dx = round(sign * s * 5)
        d.line((x, 64, x + dx, 80), fill=bico, width=3)
        d.line((x + dx, 80, x + dx + 5, 80), fill=bico, width=2)
    d.polygon(((26, 40 + bob), (18, 26 + bob), (34, 36 + bob)), fill=sombra)  # rabo
    d.polygon(((30, 44 + bob), (22, 30 + bob), (38, 40 + bob)), fill=pena)
    d.ellipse((28, 40 + bob, 66, 68 + bob), fill=pena)
    d.ellipse((34, 50 + bob, 58, 64 + bob), fill=sombra)  # asa
    d.ellipse((56, 26 + bob, 72, 44 + bob), fill=pena)  # cabeca
    d.polygon(((58, 28 + bob), (61, 20 + bob), (64, 26 + bob), (67, 20 + bob), (70, 28 + bob)), fill=crista)
    d.polygon(((71, 33 + bob), (80, 36 + bob), (71, 38 + bob)), fill=bico)  # bico
    d.ellipse((68, 39 + bob, 72, 45 + bob), fill=crista)  # barbela
    d.ellipse((65, 31 + bob, 68, 34 + bob), fill=(20, 16, 12, 255))
    return im


def capivara(i):
    """A capivara da Lagoa Maior de Tres Lagoas: corpo de barril, cabeca quadrada, perna curta."""
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = math.sin(2 * math.pi * i / N)
    bob = 1 if abs(s) > 0.7 else 0
    pelo, sombra, claro = (138, 92, 56, 255), (98, 64, 40, 255), (170, 124, 82, 255)
    nariz = (52, 36, 28, 255)
    for x, sign in ((30, 1), (38, -1), (62, -1), (70, 1)):
        dx = round(sign * s * 4)
        d.line((x, 64 + bob, x + dx, 82), fill=sombra if sign < 0 else pelo, width=6)
        d.rectangle((x + dx - 3, 80, x + dx + 3, 83), fill=nariz)
    d.ellipse((16, 38 + bob, 80, 72 + bob), fill=pelo)
    d.ellipse((22, 58 + bob, 74, 72 + bob), fill=sombra)
    d.ellipse((26, 40 + bob, 60, 52 + bob), fill=claro)
    d.rounded_rectangle((62, 30 + bob, 90, 54 + bob), radius=7, fill=pelo)  # cabeca quadrada
    d.rectangle((82, 38 + bob, 91, 50 + bob), fill=sombra)  # focinho
    d.ellipse((84, 39 + bob, 88, 43 + bob), fill=nariz)
    d.ellipse((64, 26 + bob, 72, 34 + bob), fill=sombra)  # orelha
    d.ellipse((76, 34 + bob, 80, 38 + bob), fill=(20, 16, 12, 255))  # olho
    d.line((84, 52 + bob, 89, 52 + bob), fill=nariz)  # boca
    return im


def isa_cristal(i):
    """A Isa presa no cristal do Tatu (fase 3): o sprite dela parado, de frente, dentro de um
    prisma azul com um brilho que corre de baixo para cima."""
    im = Image.new("RGBA", (F, F), (0, 0, 0, 0))
    src = Path(__file__).resolve().parent.parent / "assets" / "sprites" / "isa_japonesa.png"
    isa = Image.open(src).convert("RGBA").crop((0, 0, 64, 64))
    isa = isa.resize((84, 84), Image.NEAREST)
    im.alpha_composite(isa, (6, 12))
    # vidro so nas arestas e no topo: o gerador de sprites achata o alfa e contorna cada pixel
    # solto, entao um prisma meio transparente (ou pontilhado) esconderia a Isa
    corpo = ((48, 2), (78, 13), (80, 86), (48, 95), (16, 86), (18, 13))
    d = ImageDraw.Draw(im)
    d.polygon(((48, 2), (78, 13), (48, 20), (18, 13)), fill=(200, 236, 255, 255))
    d.line(corpo + (corpo[0],), fill=(226, 244, 255, 255), width=3)
    d.line(((48, 20), (48, 95)), fill=(180, 220, 250, 255), width=1)
    y = 86 - (i * 11) % 80  # o brilho subindo
    d.line(((22, y + 6), (74, y - 6)), fill=(255, 255, 255, 255), width=1)
    for x, yy in ((10, 70), (86, 60), (12, 30)):
        d.polygon(((x, yy - 6), (x + 3, yy), (x, yy + 6), (x - 3, yy)), fill=(160, 210, 250, 255))
    return im


def main():
    out = Path(__file__).resolve().parent.parent / "assets" / "bichos"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("bode", bode), ("galinha", galinha), ("capivara", capivara),
                     ("isa_cristal", isa_cristal)):
        strip = Image.new("RGBA", (F * N, F), (0, 0, 0, 0))
        for i in range(N):
            strip.alpha_composite(fn(i), (i * F, 0))
        strip.save(out / f"{name}.png")
        print(out / f"{name}.png")


if __name__ == "__main__":
    main()
