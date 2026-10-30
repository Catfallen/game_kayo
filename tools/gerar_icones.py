"""Desenha os icones (16x16) dos golpes do Kayo, mostrados sobre ele quando o golpe sai.

Saida: rpg-template/assets/kayo/icons/<golpe>.png. Deterministico.
Uso:  python -I tools/gerar_icones.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

S = 16
CONTORNO = (20, 14, 10, 255)


def outlined(im):
    a = np.array(im)
    solid = a[..., 3] > 0
    p = np.pad(solid, 1)
    grow = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    edge = grow & ~solid
    a[edge] = CONTORNO
    return Image.fromarray(a)


def lapada():
    """Mao aberta com riscos de movimento: a lapada."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pele, sombra = (214, 160, 112, 255), (170, 116, 76, 255)
    d.rectangle((6, 6, 12, 13), fill=pele)          # palma
    for x in (6, 8, 10, 12):                         # dedos
        d.rectangle((x, 2, x, 6), fill=pele)
    d.rectangle((4, 8, 5, 10), fill=pele)            # polegar
    d.line((7, 12, 12, 12), fill=sombra)
    for y in (4, 8, 12):                             # riscos de movimento
        d.line((1, y, 2, y), fill=(250, 240, 210, 255))
    return outlined(im)


def cruz_de_malta():
    """A cruz de malta vermelha (a do Vasco), de pontas abertas."""
    # Pixel a pixel: um braco (linha, coluna inicial, coluna final) num quadro 14x14, girado 4 vezes.
    # Largo na ponta, com o entalhe em V, estreitando ate o centro.
    arm = [(0, 3, 5), (0, 8, 10), (1, 4, 9), (2, 5, 8), (3, 6, 7), (4, 6, 7), (5, 6, 7), (6, 6, 7)]
    grid = np.zeros((14, 14), bool)
    for _ in range(4):
        for r, c0, c1 in arm:
            grid[r, c0:c1 + 1] = True
        grid = np.rot90(grid)
    a = np.zeros((S, S, 4), np.uint8)
    a[1:15, 1:15][grid] = (204, 28, 36, 255)
    for y, x in ((1, 4), (1, 5), (2, 5)):  # brilho na ponta de cima
        if a[y, x, 3]:
            a[y, x] = (244, 96, 96, 255)
    return outlined(Image.fromarray(a))


def chicotada():
    """Chicote de couro estalando, cabo de madeira."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((2, 11, 5, 13), fill=(110, 70, 40, 255))        # cabo
    couro = (150, 96, 52, 255)
    d.line(((5, 12), (8, 10), (10, 7), (12, 4), (13, 2)), fill=couro, width=1)
    d.line(((8, 11), (11, 9)), fill=couro)
    d.point((14, 1), fill=(250, 220, 120, 255))                  # estalo
    d.point((13, 0), fill=(250, 220, 120, 255))
    d.point((15, 3), fill=(250, 220, 120, 255))
    return outlined(im)


def agua_sagrada():
    """Uma gota d'agua com brilho."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    azul = (60, 140, 220, 255)
    d.polygon(((8, 1), (12, 8), (4, 8)), fill=azul)
    d.ellipse((3, 6, 12, 14), fill=azul)
    d.rectangle((5, 8, 6, 10), fill=(220, 240, 255, 255))
    return outlined(im)


def cuiabola():
    """A pokebola do sertao: metade de cima de cuia, metade de baixo clara, faixa e botao."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((1, 1, 14, 14), fill=(236, 226, 200, 255))
    d.pieslice((1, 1, 14, 14), 180, 360, fill=(150, 92, 44, 255))
    d.line((4, 4, 6, 3), fill=(196, 132, 70, 255))
    d.rectangle((1, 7, 14, 8), fill=(40, 28, 20, 255))
    d.ellipse((5, 5, 10, 10), fill=(40, 28, 20, 255))
    d.ellipse((6, 6, 9, 9), fill=(250, 246, 236, 255))
    return outlined(im)


def rajada_seca():
    """Redemoinho de vento seco levantando poeira."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    poeira, vento = (196, 160, 110, 255), (236, 230, 214, 255)
    d.arc((1, 2, 14, 8), 180, 350, fill=vento, width=2)
    d.arc((3, 6, 13, 11), 190, 360, fill=vento, width=2)
    d.arc((5, 9, 11, 14), 200, 360, fill=poeira, width=2)
    for x, y in ((2, 12), (13, 13), (12, 4)):
        d.point((x, y), fill=poeira)
    return outlined(im)


def oxente():
    """Balao de fala com '?!' - o OXENTE que deixa qualquer bicho abestado."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, 14, 11), radius=3, fill=(250, 246, 236, 255))
    d.polygon(((4, 11), (8, 11), (3, 15)), fill=(250, 246, 236, 255))
    tinta = (200, 40, 40, 255)
    d.line((5, 3, 6, 3), fill=tinta); d.point((7, 4), fill=tinta); d.point((6, 5), fill=tinta)
    d.point((6, 7), fill=tinta); d.point((6, 9), fill=tinta)                    # ?
    d.line((10, 3, 10, 7), fill=tinta); d.point((10, 9), fill=tinta)          # !
    return outlined(im)


def main():
    out = Path(__file__).resolve().parent.parent / "rpg-template" / "assets" / "kayo" / "icons"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("lapada_da_misera", lapada), ("cruz_de_malta", cruz_de_malta),
                     ("chicotada_do_lampiao", chicotada), ("agua_sagrada", agua_sagrada),
                     ("cuiabola", cuiabola), ("rajada_seca", rajada_seca), ("oxente", oxente)):
        fn().save(out / f"{name}.png")
        print(out / f"{name}.png")


if __name__ == "__main__":
    main()
