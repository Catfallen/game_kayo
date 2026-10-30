"""Desenha os tiles do Japao (32x32) usados na fase 3: o castelo, as cerejeiras e o salao do chefe.

Saida: rpg-template/data/imports/tiles/lpc32/japao.png, cortada pelo banco data/tiles/lpc32.json,
como a cidade.png do tools/gerar_tiles_cidade.py (daqui vem o jeito de gravar os bancos, o espelho
de 16px no gb16.json e a regra de que pedaco de figura grande sem furo vira chao). Deterministico.

Linhas: chao (madeira, tatame, pedras, cascalho, muro, telhado, shoji, ponte, ceu da noite),
jardim (cerejeira, petalas, lanternas, bambu, pinheiro), salao (pilar, biombo, estandarte,
cristais, taiko), o portao torii (3x2) e o castelo inteiro (6x5), desenhado de uma vez e cortado.

Uso:  python -I tools/gerar_tiles_japao.py   (depois o tools/gen_sprites.gd do template)
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from gerar_tiles_sertao import CINZA, MADEIRA, OSSO, T, VERDE, outlined, rig_rows, speckle

COLS = 10
FILE = "japao.png"

TATAME = [(132, 134, 70), (164, 164, 92), (192, 188, 118), (216, 210, 148)]
ESCURA = [(54, 30, 22), (82, 48, 32), (110, 68, 44), (140, 92, 60)]  # madeira encerada do castelo
PEDRA = [(70, 72, 80), (100, 102, 112), (132, 134, 144), (166, 168, 176)]
CASCALHO = [(150, 146, 136), (176, 172, 162), (198, 194, 184), (220, 216, 206)]
MURO = [(196, 192, 186), (220, 216, 210), (236, 234, 228), (248, 248, 244)]
TELHA = [(30, 34, 50), (46, 52, 72), (64, 72, 96), (92, 100, 126)]
PAPEL = [(214, 206, 180), (232, 226, 204), (244, 240, 224)]
LACA = [(120, 20, 24), (170, 36, 36), (212, 64, 52), (236, 110, 90)]  # vermelho do torii
SAKURA = [(196, 100, 144), (232, 144, 182), (248, 186, 210), (255, 222, 236)]
CRISTAL = [(60, 70, 150), (100, 140, 214), (160, 206, 248), (226, 244, 255)]
NOITE = [(14, 12, 30), (26, 22, 50), (40, 34, 70)]
OURO = [(170, 120, 20), (226, 180, 50), (252, 226, 120)]
BRANCO = (246, 246, 240)

GROUND = ["piso_castelo", "tatame", "pedra_caminho", "cascalho", "muro_castelo", "telhado_jp", "shoji",
          "ponte", "ceu_noite", "ceu_lua"]
JARDIM = ["sakura", "petalas", "lanterna_pedra", "bambu", "pinheiro", "lanterna_papel", "cerca_bambu",
          "placa_jp"]
SALAO = ["pilar", "biombo", "estandarte", "cristal", "cristal_chao", "vaso_jp", "taiko", "katana"]
TORII_W, TORII_H = 3, 2
TORII = [[f"torii_{y}{x}" for x in range(TORII_W)] for y in range(TORII_H)]
CASTELO_W, CASTELO_H = 6, 5
CASTELO = [[f"castelo_{y}{x}" for x in range(CASTELO_W)] for y in range(CASTELO_H)]
# a porta do castelo: os dois tiles do meio da ultima linha, onde fica o warp
PORTA = {"castelo_42", "castelo_43"}

RAMPS = {
    "piso_castelo": "leather", "tatame": "terrain_grass", "pedra_caminho": "stone", "cascalho": "stone",
    "muro_castelo": "skin_light", "telhado_jp": "stone", "shoji": "skin_light", "ponte": "skin_dark",
    "ceu_noite": "terrain_water", "ceu_lua": "terrain_water",
    "sakura": "skin_dark", "petalas": "skin_dark", "lanterna_pedra": "stone", "bambu": "terrain_bush",
    "pinheiro": "terrain_bush", "lanterna_papel": "skin_dark", "cerca_bambu": "terrain_bush",
    "placa_jp": "leather",
    "pilar": "leather", "biombo": "skin_light", "estandarte": "skin_dark", "cristal": "terrain_water",
    "cristal_chao": "terrain_water", "vaso_jp": "stone", "taiko": "leather", "katana": "stone",
}
RAMPS.update({n: "skin_dark" for row in TORII for n in row})
RAMPS.update({n: "stone" for row in CASTELO for n in row})
# o que da para pisar fica de fora: o chao de andar, as petalas, os cristaizinhos, o vao do torii
# (por baixo da trave, os dois tiles do meio) e
# a porta do castelo
SOLID = ({"muro_castelo", "telhado_jp", "shoji", "ceu_noite", "ceu_lua"}
         | (set(JARDIM) | set(SALAO)) - {"petalas", "cristal_chao"}
         | {n for row in TORII for n in row} - {"torii_01", "torii_11"}
         | {n for row in CASTELO for n in row} - PORTA)


def opaque(img):
    out = np.zeros((T, T, 4), np.uint8)
    out[..., :3] = img
    out[..., 3] = 255
    return out


def ground_tile(name, rng):
    if name == "piso_castelo":  # tabuas largas enceradas, emendas desencontradas
        img = speckle(rng, ESCURA, 2, 0.05)
        for y in (0, 8, 16, 24):
            img[y] = ESCURA[0]
            off = 10 if (y // 8) % 2 else 22
            img[y:y + 8, off] = ESCURA[0]
            img[y + 2, :] = np.where(rng.random((T, 1)) < 0.3, ESCURA[3], img[y + 2, :])
    elif name == "tatame":  # palha com a borda de pano escura
        img = speckle(rng, TATAME, 2, 0.05)
        for x in range(1, T, 3):
            img[:, x] = TATAME[1]
        img[:2] = (40, 50, 34)
        img[-2:] = (40, 50, 34)
    elif name == "pedra_caminho":  # lajes de pedra do jardim, com musgo nas juntas
        img = speckle(rng, VERDE, 1, 0.1)
        for box in ((1, 1, 14, 13), (16, 2, 30, 14), (2, 16, 12, 30), (14, 17, 30, 30)):
            x0, y0, x1, y1 = box
            img[y0:y1, x0:x1] = PEDRA[2]
            img[y0, x0:x1] = PEDRA[3]
            img[y1 - 1, x0:x1] = PEDRA[1]
            img[y0:y1, x1 - 1] = PEDRA[1]
    elif name == "cascalho":  # o cascalho rastelado do jardim zen
        img = speckle(rng, CASCALHO, 2, 0.15)
        for y in range(3, T, 6):
            img[y] = CASCALHO[0]
    elif name == "muro_castelo":  # reboco branco sobre a base de pedra
        img = speckle(rng, MURO, 2, 0.04)
        img[20:] = PEDRA[1]
        for x0 in range(0, T, 8):
            img[20:, x0] = PEDRA[0]
        img[26, :] = PEDRA[0]
        img[19] = ESCURA[1]
    elif name == "telhado_jp":  # telhas escuras em escama
        img = np.zeros((T, T, 3), np.uint8)
        img[:] = TELHA[1]
        for y in range(0, T, 6):
            img[y] = TELHA[0]
            for x in range(0, T, 8):
                xx = (x + (4 if (y // 6) % 2 else 0)) % T
                img[y + 1:y + 5, xx] = TELHA[0]
                img[y + 1, (xx + 2) % T:(xx + 6) % T or T] = TELHA[3]
    elif name == "shoji":  # papel de arroz numa grade de madeira
        img = np.zeros((T, T, 3), np.uint8)
        img[:] = PAPEL[2]
        img[16:] = PAPEL[1]
        for k in (0, 10, 21):
            img[:, k] = ESCURA[2]
        for k in (0, 8, 16, 24):
            img[k] = ESCURA[2]
        img[:, -1] = ESCURA[1]
        img[-3:] = ESCURA[1]
    elif name == "ponte":  # a ponte de madeira laqueada sobre o lago
        img = speckle(rng, MADEIRA, 2, 0.06)
        for y in range(0, T, 5):
            img[y] = MADEIRA[0]
        img[:, :3] = LACA[1]
        img[:, -3:] = LACA[1]
        img[:, 3] = LACA[0]
        img[:, -4] = LACA[0]
    elif name in ("ceu_noite", "ceu_lua"):  # o ceu roxo da noite, com estrelas (e a lua cheia)
        img = np.zeros((T, T, 3), np.uint8)
        for y in range(T):
            img[y] = NOITE[min(2, y // 12)]
        for _ in range(4):
            y, x = int(rng.integers(1, T - 1)), int(rng.integers(1, T - 1))
            img[y, x] = (220, 220, 240)
        if name == "ceu_lua":
            yy, xx = np.mgrid[0:T, 0:T]
            disc = (yy - 14) ** 2 + (xx - 16) ** 2
            img[disc <= 100] = (250, 242, 214)
            img[(disc <= 100) & ((yy - 11) ** 2 + (xx - 13) ** 2 <= 9)] = (226, 216, 186)
            img[(disc > 100) & (disc <= 130)] = (90, 80, 110)
    else:
        raise ValueError(name)
    return opaque(img)


def copa_sakura(d, rng, box, flores=40):
    x0, y0, x1, y1 = box
    d.ellipse(box, fill=SAKURA[0])
    d.ellipse((x0 + 2, y0 + 1, x1 - 3, y1 - 4), fill=SAKURA[1])
    for _ in range(flores):
        x, y = int(rng.integers(x0 + 2, x1 - 2)), int(rng.integers(y0 + 2, y1 - 3))
        d.rectangle((x, y, x + 1, y + 1), fill=SAKURA[2 + int(rng.integers(0, 2))])


def jardim_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "sakura":  # a cerejeira em flor, tronco escuro e torto
        d.line((16, 30, 15, 18), fill=ESCURA[1], width=4)
        d.line((15, 20, 8, 13), fill=ESCURA[1], width=2)
        d.line((16, 19, 24, 12), fill=ESCURA[1], width=2)
        copa_sakura(d, rng, (0, 0, 31, 22))
        for x, y in ((6, 26), (22, 27), (27, 24)):  # petalas ja caidas no pe
            d.point((x, y), fill=SAKURA[2])
    elif name == "petalas":  # chao coberto de petalas: da para pisar
        for _ in range(16):
            x, y = int(rng.integers(1, T - 3)), int(rng.integers(1, T - 2))
            d.rectangle((x, y, x + 1, y), fill=SAKURA[int(rng.integers(1, 4))])
        for x, y in ((6, 8), (20, 22)):  # um montinho com petala escura e uma folha
            d.rectangle((x, y, x + 3, y + 2), fill=SAKURA[0])
            d.rectangle((x + 1, y, x + 2, y + 1), fill=SAKURA[3])
            d.point((x + 4, y + 2), fill=VERDE[2])
        return np.array(im)
    elif name == "lanterna_pedra":  # o toro de pedra, com a luz acesa
        d.rectangle((12, 25, 19, 30), fill=PEDRA[1])
        d.rectangle((14, 18, 17, 25), fill=PEDRA[2])
        d.rectangle((9, 15, 22, 18), fill=PEDRA[1])
        d.rectangle((11, 9, 20, 15), fill=PEDRA[2])
        d.rectangle((13, 10, 18, 14), fill=OURO[2])
        d.polygon(((6, 9), (25, 9), (19, 4), (12, 4)), fill=PEDRA[1])
        d.rectangle((15, 1, 16, 4), fill=PEDRA[2])
    elif name == "bambu":
        for x, c in ((6, VERDE[2]), (14, VERDE[3]), (22, VERDE[2])):
            d.rectangle((x, 1, x + 3, 30), fill=c)
            for y in range(5, 30, 8):
                d.line((x, y, x + 3, y), fill=VERDE[0])
            d.line((x + 3, 8, x + 7, 5), fill=VERDE[1], width=2)
    elif name == "pinheiro":  # pinheiro de jardim, podado em nuvens
        d.line((16, 30, 14, 14), fill=ESCURA[1], width=3)
        d.line((15, 20, 24, 16), fill=ESCURA[1], width=2)
        for box in ((3, 4, 20, 13), (14, 11, 30, 19), (6, 15, 18, 22)):
            d.ellipse(box, fill=VERDE[1])
            d.ellipse((box[0] + 2, box[1] + 1, box[2] - 2, box[3] - 3), fill=VERDE[2])
    elif name == "lanterna_papel":  # a lanterna de papel vermelha, pendurada
        d.line((16, 0, 16, 5), fill=CINZA[1])
        d.rectangle((12, 5, 19, 6), fill=(30, 30, 30))
        d.ellipse((7, 6, 24, 26), fill=LACA[1])
        for y in (10, 14, 18, 22):
            d.line((9, y, 22, y), fill=LACA[0])
        d.ellipse((12, 10, 19, 20), fill=LACA[3])
        d.rectangle((12, 25, 19, 27), fill=(30, 30, 30))
    elif name == "cerca_bambu":  # cerca baixa de bambu amarrado, emenda com a vizinha
        d.rectangle((0, 12, 31, 14), fill=VERDE[3])
        d.rectangle((0, 22, 31, 24), fill=VERDE[3])
        for x in range(2, T, 6):
            d.rectangle((x, 8, x + 2, 29), fill=VERDE[2])
        return np.array(open_sides(im, left=True, right=True))
    elif name == "placa_jp":  # placa de madeira com kanji de mentira
        d.rectangle((14, 20, 17, 30), fill=ESCURA[2])
        d.rectangle((6, 2, 25, 21), fill=MADEIRA[3])
        d.rectangle((7, 3, 24, 20), outline=ESCURA[1])
        for y, w in ((6, 8), (10, 6), (14, 9)):
            d.line((16 - w // 2, y, 16 + w // 2, y), fill=ESCURA[0], width=2)
        d.line((16, 5, 16, 18), fill=ESCURA[0])
    else:
        raise ValueError(name)
    return outlined(im)


def open_sides(im, left=False, right=False):
    """Contorno, menos no lado que emenda com o vizinho."""
    a = outlined(im)
    raw = np.array(im)
    if right:
        a[:, -1] = raw[:, -1]
    if left:
        a[:, 0] = raw[:, 0]
    return a


def cristal(d, x, y, h, w, ramp=CRISTAL):
    """Um cristal em ponta: corpo, face clara e brilho."""
    d.polygon(((x, y + h), (x - w, y + h // 3), (x, y), (x + w, y + h // 3)), fill=ramp[1])
    d.polygon(((x, y + h), (x, y), (x + w, y + h // 3)), fill=ramp[2])
    d.line((x, y + 2, x, y + h // 2), fill=ramp[3])


def salao_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "pilar":  # pilar de madeira laqueada com base de pedra
        d.rectangle((10, 0, 21, 27), fill=LACA[1])
        d.rectangle((10, 0, 12, 27), fill=LACA[2])
        d.rectangle((19, 0, 21, 27), fill=LACA[0])
        d.rectangle((8, 26, 23, 30), fill=PEDRA[1])
        d.rectangle((9, 3, 22, 5), fill=OURO[1])
    elif name == "biombo":  # biombo pintado com uma montanha e um galho de sakura
        for k, x in enumerate((1, 9, 17, 25)):
            d.rectangle((x, 4, x + 6, 28), fill=PAPEL[2] if k % 2 == 0 else PAPEL[1])
            d.rectangle((x, 4, x + 6, 28), outline=ESCURA[1])
        d.polygon(((3, 24), (12, 11), (21, 24)), fill=PEDRA[1])
        d.polygon(((10, 14), (12, 11), (14, 14)), fill=BRANCO)
        for x, y in ((20, 9), (23, 12), (26, 8), (28, 13)):
            d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=SAKURA[1])
        d.line((19, 14, 30, 7), fill=ESCURA[1])
    elif name == "estandarte":  # estandarte do castelo com o brasao do tatu
        d.line((5, 1, 5, 30), fill=ESCURA[1], width=2)
        d.rectangle((6, 3, 26, 26), fill=TELHA[2])
        d.rectangle((6, 3, 26, 5), fill=OURO[1])
        d.ellipse((10, 9, 22, 21), fill=CRISTAL[2])
        d.ellipse((13, 12, 19, 18), fill=TELHA[1])
    elif name == "cristal":  # um aglomerado de cristal crescendo do chao
        cristal(d, 9, 10, 20, 5)
        cristal(d, 21, 6, 24, 6)
        cristal(d, 15, 2, 28, 6)
    elif name == "cristal_chao":  # cristaizinhos no chao: da para pisar
        for x, y, h in ((6, 18, 9), (14, 22, 7), (24, 16, 10), (20, 26, 5)):
            cristal(d, x, y, h, 2)
        return np.array(im)
    elif name == "vaso_jp":  # vaso azul e branco com um galho
        d.polygon(((10, 14), (22, 14), (25, 22), (20, 30), (12, 30), (7, 22)), fill=BRANCO)
        d.line((9, 20, 23, 20), fill=CRISTAL[0], width=2)
        d.line((12, 25, 20, 25), fill=CRISTAL[0])
        d.line((16, 14, 13, 3), fill=ESCURA[1])
        d.line((15, 8, 22, 4), fill=ESCURA[1])
        for x, y in ((13, 3), (22, 4), (18, 7)):
            d.ellipse((x - 1, y - 1, x + 2, y + 2), fill=SAKURA[1])
    elif name == "taiko":  # o tambor grande no suporte
        d.rectangle((5, 24, 26, 30), fill=ESCURA[1])
        d.ellipse((4, 5, 27, 26), fill=LACA[1])
        d.ellipse((7, 8, 24, 23), fill=OSSO[2])
        d.ellipse((12, 13, 19, 18), fill=LACA[0])
        for x, y in ((5, 15), (26, 15), (15, 5), (15, 25)):
            d.point((x, y), fill=OURO[2])
    elif name == "katana":  # duas espadas no suporte
        d.rectangle((3, 26, 28, 29), fill=ESCURA[1])
        d.rectangle((5, 12, 7, 26), fill=ESCURA[1])
        d.rectangle((24, 12, 26, 26), fill=ESCURA[1])
        for y in (13, 19):
            d.line((3, y, 28, y - 2), fill=(30, 30, 34), width=2)
            d.line((20, y - 1, 28, y - 2), fill=OURO[1], width=2)
    else:
        raise ValueError(name)
    return outlined(im)


def torii():
    """O portao torii, 3x2 tiles: dois pilares vermelhos e a dupla trave em cima."""
    im = Image.new("RGBA", (TORII_W * T, TORII_H * T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = TORII_W * T
    d.polygon(((0, 6), (w - 1, 6), (w - 6, 14), (5, 14)), fill=(28, 24, 26))  # kasagi, preto
    d.rectangle((4, 2, w - 5, 7), fill=(28, 24, 26))
    d.rectangle((6, 14, w - 7, 18), fill=LACA[1])
    d.rectangle((6, 24, w - 7, 28), fill=LACA[1])  # nuki
    d.rectangle((44, 17, 51, 25), fill=LACA[0])  # a placa do meio
    # a corda sagrada (shimenawa) com os papeis em zigue-zague, pendurada no vao do meio
    d.line((34, 32, 61, 32), fill=OSSO[2], width=3)
    for x in (38, 47, 56):
        d.line((x, 34, x + 2, 38, x, 42, x + 2, 46), fill=BRANCO, width=2)
    for x0 in (12, w - 24):
        d.rectangle((x0, 14, x0 + 11, 60), fill=LACA[1])
        d.rectangle((x0, 14, x0 + 3, 60), fill=LACA[2])
        d.rectangle((x0 + 9, 14, x0 + 11, 60), fill=LACA[0])
        d.rectangle((x0 - 1, 56, x0 + 12, 63), fill=(28, 24, 26))
    return outlined(im)


def castelo():
    """O castelo inteiro, 6x5 tiles: base de pedra, tres andares de muro branco e telhados que se
    abrem nas pontas, com os peixes dourados no topo. A porta fica no meio da base."""
    W, H = CASTELO_W * T, CASTELO_H * T
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2

    def telhado(y, half, depth):
        # beiral curvo: as pontas sobem um pouco
        d.polygon(((cx - half - 6, y + depth - 4), (cx - half, y + depth), (cx + half, y + depth),
                   (cx + half + 6, y + depth - 4), (cx + half - 10, y), (cx - half + 10, y)),
                  fill=TELHA[1])
        d.line((cx - half - 6, y + depth - 4, cx + half + 6, y + depth - 4), fill=TELHA[3])
        for x in range(cx - half + 12, cx + half - 10, 6):
            d.line((x, y + 2, x - 2, y + depth - 2), fill=TELHA[0])
        d.line((cx - half - 6, y + depth - 4, cx - half - 8, y + depth - 9), fill=TELHA[1], width=3)
        d.line((cx + half + 6, y + depth - 4, cx + half + 8, y + depth - 9), fill=TELHA[1], width=3)

    def andar(y0, y1, half, janelas):
        d.rectangle((cx - half, y0, cx + half, y1), fill=MURO[2])
        d.line((cx - half, y1, cx + half, y1), fill=MURO[0])
        for k in range(janelas):
            x = cx - half + 10 + k * ((2 * half - 20) // max(janelas - 1, 1)) - 4
            d.rectangle((x, y0 + 4, x + 7, y0 + 10), fill=(28, 24, 26))
            d.line((x + 2, y0 + 4, x + 2, y0 + 10), fill=ESCURA[2])
            d.line((x + 5, y0 + 4, x + 5, y0 + 10), fill=ESCURA[2])

    # a base de pedra (ishigaki), inclinada
    d.polygon(((4, H - 1), (W - 5, H - 1), (W - 16, 112), (15, 112)), fill=PEDRA[1])
    for y in range(116, H, 7):
        lado = 15 - (y - 112) * 11 // (H - 1 - 112)  # a borda inclinada nessa altura
        for x in range(lado + 3 + (y // 7) % 2 * 6, W - lado - 12, 12):
            d.line((x, y, x + 8, y), fill=PEDRA[0])
            d.point((x + 2, y + 2), fill=PEDRA[3])
    # a porta grande de madeira com ferragens, no meio da base (os tiles castelo_42 e castelo_43)
    d.rectangle((cx - 22, 128, cx + 21, H - 1), fill=ESCURA[1])
    d.rectangle((cx - 22, 128, cx + 21, 131), fill=(28, 24, 26))
    d.line((cx, 132, cx, H - 1), fill=(28, 24, 26))
    for x in (cx - 16, cx - 8, cx + 6, cx + 14):
        for y in (138, 148):
            d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=OURO[1])
    # terreo
    andar(84, 112, 76, 6)
    telhado(70, 82, 16)
    # segundo andar
    andar(50, 74, 56, 4)
    telhado(36, 64, 16)
    # torre do topo
    andar(22, 40, 34, 2)
    telhado(6, 42, 18)
    # os shachihoko dourados nas pontas da cumeeira
    for sx in (cx - 30, cx + 26):
        d.polygon(((sx, 8), (sx + 4, 0), (sx + 5, 8)), fill=OURO[1])
    d.line((cx - 30, 7, cx + 30, 7), fill=TELHA[3], width=2)
    # duas petalas passando pelos cantos de cima, que de outro jeito seriam so ceu
    for px, py in ((10, 12), (18, 22), (W - 14, 10), (W - 22, 20)):
        d.rectangle((px, py, px + 2, py + 1), fill=SAKURA[1])
        d.point((px + 1, py), fill=SAKURA[3])
    # brilho de cristal saindo pela janela mais alta: o chefe esta la dentro
    d.rectangle((cx - 4, 27, cx + 3, 33), fill=CRISTAL[2])
    return outlined(im)


_FIGURAS = {}


def figura_tile(name, rng):
    if not _FIGURAS:
        _FIGURAS["torii"], _FIGURAS["castelo"] = torii(), castelo()
    fig = _FIGURAS["torii" if name.startswith("torii") else "castelo"]
    y, x = int(name[-2]), int(name[-1])
    return fig[y * T:(y + 1) * T, x * T:(x + 1) * T]


def main():
    root = Path(__file__).resolve().parent.parent
    out = root / "rpg-template" / "data" / "imports" / "tiles" / "lpc32" / FILE
    rows = [(0, GROUND, ground_tile), (1, JARDIM, jardim_tile), (2, SALAO, salao_tile),
            (3, TORII[0] + TORII[1], figura_tile)]
    rows += [(4 + y, CASTELO[y], figura_tile) for y in range(CASTELO_H)]
    sheet = np.zeros((T * len(rows), T * COLS, 4), np.uint8)
    rig, cells = [], []
    for row, names, draw in rows:
        for i, name in enumerate(names):
            tile = np.asarray(draw(name, np.random.default_rng(5000 + row * 100 + i)))
            sheet[row * T:(row + 1) * T, i * T:(i + 1) * T] = tile
            # um pedaco de figura grande sem nenhum furo e chao (o template recusa decoracao opaca)
            decor = row > 0 and not (row >= 3 and tile[..., 3].min() == 255)
            entry = {"id": name, "ramp": RAMPS[name], "solid": name in SOLID}
            if decor:
                entry["decor"] = True
            rig.append(dict(entry, rows=rig_rows(tile, decor)))
            cells.append({"id": name, "from": FILE, "cell": [i, row], "solid": name in SOLID, "decor": decor})
    Image.fromarray(sheet).save(out, optimize=False)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    write_banks(root / "rpg-template" / "data" / "tiles", rig, cells, sha)
    print(out)
    print("sha256", sha)


def _load(path):
    raw = path.read_text(encoding="utf-8")
    bank = json.loads(raw)
    assert json.dumps(bank, indent="\t", ensure_ascii=False) + "\n" == raw, f"formato de {path.name} mudou"
    return bank


def _save(path, bank):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(bank, indent="\t", ensure_ascii=False) + "\n")


def write_banks(tiles_dir, rig, cells, sha):
    lpc = _load(tiles_dir / "lpc32.json")
    entry = {"file": FILE, "sha256": sha, "authors": ["Projeto de faculdade game_kayo"],
             "licenses": ["CC-BY 4.0"], "urls": [],
             "notes": "Desenhado por game_kayo/tools/gerar_tiles_japao.py; o castelo japones da fase 3."}
    old = {t["id"] for t in lpc["tiles"] if t.get("from") == FILE}
    lpc["files"] = [f for f in lpc["files"] if f["file"] != FILE] + [entry]
    lpc["tiles"] = [t for t in lpc["tiles"] if t.get("from") != FILE] + cells
    _save(tiles_dir / "lpc32.json", lpc)
    gb = _load(tiles_dir / "gb16.json")
    ours = {t["id"] for t in rig} | old
    gb["tiles"] = [t for t in gb["tiles"] if t["id"] not in ours] + rig
    _save(tiles_dir / "gb16.json", gb)
    print(f"bancos: +{len(cells)} tiles do Japao")


if __name__ == "__main__":
    main()
