"""Desenha os tiles de sertao (32x32) usados nas fases do Nordeste.

Saida: rpg-template/data/imports/tiles/lpc32/sertao.png, uma folha de 8 colunas, cortada pelo
banco data/tiles/lpc32.json (cada tile aponta uma celula [coluna, linha]). Deterministico:
o mesmo script sempre gera os mesmos bytes, e o sha256 impresso vai para o banco.

Chao (linha 0) e opaco; decoracao (linha 1) e moveis da casa (linha 2) tem fundo transparente e
sao desenhados por cima do chao. O script tambem atualiza os bancos lpc32 (sha256 + celulas) e
gb16 (versao 16px), entao basta roda-lo e depois o tools/gen_sprites.gd do template.

Uso:  python -I tools/gerar_tiles_sertao.py
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

T = 32
COLS = 8

GROUND = ["terra", "terra_alt", "estrada", "pedra", "parede_madeira", "piso_madeira", "porta", "telhado"]
DECOR = ["mandacaru", "arbusto_seco", "arvore_seca", "calango", "caveira", "poste", "placa", "cerca"]

TERRA = [(122, 84, 46), (156, 110, 62), (181, 134, 80), (201, 158, 102)]
AREIA = [(170, 132, 84), (204, 168, 112), (222, 190, 136), (236, 210, 160)]
PEDRA = [(70, 62, 58), (104, 94, 86), (138, 126, 112), (168, 156, 140)]
MADEIRA = [(58, 36, 22), (98, 62, 36), (138, 92, 54), (170, 122, 76)]
TELHA = [(92, 38, 26), (140, 62, 40), (176, 90, 58), (204, 120, 80)]
VERDE = [(34, 58, 36), (56, 92, 52), (86, 126, 66), (124, 160, 86)]
SECO = [(70, 54, 40), (110, 88, 64), (150, 126, 92), (186, 164, 124)]
OSSO = [(120, 110, 96), (188, 178, 160), (226, 218, 200), (248, 244, 232)]
CINZA = [(40, 40, 46), (86, 86, 94)]
CONTORNO = (20, 14, 10)


def speckle(rng, ramp, base_idx, density):
    img = np.zeros((T, T, 3), np.uint8)
    img[:] = ramp[base_idx]
    r = rng.random((T, T))
    img[r < density] = ramp[max(0, base_idx - 1)]
    img[r > 1 - density] = ramp[min(len(ramp) - 1, base_idx + 1)]
    return img


def crack(img, rng, color, n):
    for _ in range(n):
        y, x = int(rng.integers(2, T - 2)), int(rng.integers(2, T - 2))
        for _ in range(int(rng.integers(5, 11))):
            img[y % T, x % T] = color
            y += int(rng.integers(-1, 2))
            x += int(rng.choice([-1, 1]))


def ground_tile(name, rng):
    if name == "terra":
        img = speckle(rng, TERRA, 2, 0.10)
        crack(img, rng, TERRA[0], 3)
    elif name == "terra_alt":
        img = speckle(rng, TERRA, 2, 0.10)
        crack(img, rng, TERRA[0], 1)
        for _ in range(5):  # pedrinhas
            y, x = int(rng.integers(2, T - 3)), int(rng.integers(2, T - 3))
            img[y:y + 2, x:x + 2] = PEDRA[2]
            img[y + 1, x + 1] = PEDRA[1]
        for _ in range(3):  # capim seco
            y, x = int(rng.integers(6, T - 2)), int(rng.integers(2, T - 4))
            for k in range(4):
                img[y - (k % 2) - 1:y, x + k] = SECO[3]
    elif name == "estrada":
        img = speckle(rng, AREIA, 2, 0.12)
        img[:, 7:9] = np.where(rng.random((T, 2, 1)) < 0.6, AREIA[1], img[:, 7:9])
        img[:, 23:25] = np.where(rng.random((T, 2, 1)) < 0.6, AREIA[1], img[:, 23:25])
    elif name == "pedra":
        img = speckle(rng, PEDRA, 1, 0.15)
        for _ in range(4):
            cy, cx, r = int(rng.integers(4, T - 4)), int(rng.integers(4, T - 4)), int(rng.integers(5, 9))
            yy, xx = np.mgrid[:T, :T]
            d = (yy - cy) ** 2 + (xx - cx) ** 2
            img[d < r * r] = PEDRA[2]
            img[(d < r * r) & (yy < cy - r // 3)] = PEDRA[3]
            img[(d >= r * r) & (d < (r + 1) ** 2)] = PEDRA[0]
    elif name == "parede_madeira":
        img = speckle(rng, MADEIRA, 2, 0.08)
        for x in range(0, T, 8):
            img[:, x] = MADEIRA[0]
            img[:, x + 1] = MADEIRA[1]
        img[3:5] = MADEIRA[0]
        img[27:29] = MADEIRA[0]
        for x in range(4, T, 8):
            img[6, x] = CINZA[1]
            img[25, x] = CINZA[1]
    elif name == "piso_madeira":
        img = speckle(rng, MADEIRA, 3, 0.08)
        for y in range(0, T, 8):
            img[y] = MADEIRA[1]
        for y, x in ((0, 12), (8, 26), (16, 5), (24, 19)):
            img[y:y + 8, x] = MADEIRA[1]
    elif name == "porta":
        img = speckle(rng, MADEIRA, 1, 0.06)
        img[:, :4] = MADEIRA[0]
        img[:, -4:] = MADEIRA[0]
        img[:3] = MADEIRA[0]
        for x in (10, 16, 22):
            img[3:, x] = MADEIRA[0]
        img[16:18, 24:26] = OSSO[2]
    elif name == "telhado":
        img = speckle(rng, TELHA, 2, 0.06)
        for y in range(0, T, 6):
            img[y] = TELHA[0]
            img[y + 1] = TELHA[3]
            off = 0 if (y // 6) % 2 == 0 else 4
            for x in range(off, T, 8):
                img[y:y + 6, x] = TELHA[1]
    else:
        raise ValueError(name)
    out = np.zeros((T, T, 4), np.uint8)
    out[..., :3] = img
    out[..., 3] = 255
    return out


def outlined(img):
    """Contorno escuro de 1px em volta do que foi desenhado (o resto continua transparente)."""
    a = np.array(img)
    solid = a[..., 3] > 0
    # borda replicada (e nao circular): um movel que encosta na borda emenda com o vizinho
    p = np.pad(solid, 1, mode="edge")
    grow = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    edge = grow & ~solid
    a[edge, :3] = CONTORNO
    a[edge, 3] = 255
    return a


def decor_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "mandacaru":
        d.rectangle((13, 3, 18, 29), fill=VERDE[2])
        d.rectangle((5, 10, 9, 20), fill=VERDE[2])
        d.rectangle((5, 18, 13, 21), fill=VERDE[2])
        d.rectangle((22, 6, 26, 16), fill=VERDE[2])
        d.rectangle((18, 14, 26, 17), fill=VERDE[2])
        for x0, y0, y1 in ((13, 3, 29), (5, 10, 20), (22, 6, 16)):
            d.line((x0, y0, x0, y1), fill=VERDE[1])
            d.line((x0 + 2, y0 + 1, x0 + 2, y1 - 1), fill=VERDE[3])
        for _ in range(14):  # espinhos
            y, x = int(rng.integers(4, 28)), int(rng.choice([12, 19, 4, 10, 21, 27]))
            if im.getpixel((min(31, x + 1), y))[3] or im.getpixel((max(0, x - 1), y))[3]:
                d.point((x, y), fill=OSSO[3])
        d.point((15, 2), fill=(214, 84, 120))
        d.point((16, 2), fill=(214, 84, 120))
    elif name == "arbusto_seco":
        for _ in range(26):
            x0, y0 = 16 + int(rng.integers(-3, 4)), 28
            x1, y1 = int(rng.integers(4, 28)), int(rng.integers(10, 26))
            d.line((x0, y0, x1, y1), fill=SECO[int(rng.integers(1, 4))])
        d.rectangle((14, 27, 18, 29), fill=SECO[0])
    elif name == "arvore_seca":
        d.rectangle((14, 14, 17, 30), fill=SECO[1])
        d.line((15, 14, 15, 30), fill=SECO[2])
        for x0, y0, x1, y1 in ((15, 16, 6, 6), (16, 14, 25, 4), (15, 20, 4, 14), (16, 18, 27, 12),
                               (9, 9, 5, 3), (22, 7, 27, 6), (15, 14, 15, 2), (6, 6, 2, 7)):
            d.line((x0, y0, x1, y1), fill=SECO[1], width=2 if y0 > 12 else 1)
        d.line((12, 30, 20, 30), fill=SECO[0])
    elif name == "calango":
        body = [(9, 18), (12, 16), (16, 16), (20, 17), (23, 18)]
        d.line(body, fill=VERDE[2], width=3)
        d.line((23, 18, 28, 21, 30, 21), fill=VERDE[1])  # rabo
        d.ellipse((5, 15, 10, 20), fill=VERDE[3])  # cabeca
        for x, y0, y1 in ((11, 16, 13), (12, 19, 22), (19, 16, 13), (20, 19, 22)):
            d.line((x, y0, x - 2, y1), fill=VERDE[1])
        d.point((7, 16), fill=CONTORNO)
        for x in (13, 16, 19):
            d.point((x, 17), fill=(196, 120, 52))
    elif name == "caveira":
        d.ellipse((11, 14, 21, 24), fill=OSSO[2])
        d.rectangle((13, 22, 19, 27), fill=OSSO[2])
        d.line((11, 16, 6, 13, 4, 9), fill=OSSO[3], width=2)
        d.line((21, 16, 26, 13, 28, 9), fill=OSSO[3], width=2)
        d.point((14, 18), fill=CONTORNO); d.point((18, 18), fill=CONTORNO)
        d.point((14, 19), fill=CONTORNO); d.point((18, 19), fill=CONTORNO)
        d.line((15, 25, 17, 25), fill=OSSO[0])
    elif name == "poste":
        d.rectangle((14, 4, 17, 30), fill=MADEIRA[2])
        d.line((14, 4, 14, 30), fill=MADEIRA[1])
        d.rectangle((7, 6, 24, 8), fill=MADEIRA[1])
        for x in (8, 15, 23):
            d.rectangle((x, 4, x + 1, 5), fill=OSSO[2])
        d.line((0, 7, 7, 7), fill=CINZA[0])  # fios: emendam no poste vizinho
        d.line((24, 7, 31, 7), fill=CINZA[0])
    elif name == "placa":
        d.rectangle((14, 16, 17, 30), fill=CINZA[1])
        d.rectangle((3, 4, 28, 17), fill=(32, 104, 64))
        d.rectangle((4, 5, 27, 16), outline=OSSO[3])
        d.line((7, 8, 18, 8), fill=OSSO[3])
        d.line((7, 12, 15, 12), fill=OSSO[3])
        d.polygon(((21, 9), (25, 11), (21, 13)), fill=OSSO[3])
    elif name == "cerca":
        for x in (3, 15, 27):
            d.rectangle((x, 10, x + 2, 29), fill=MADEIRA[2])
            d.line((x, 10, x, 29), fill=MADEIRA[1])
        for y in (14, 22):
            d.rectangle((0, y, 31, y + 1), fill=MADEIRA[3])
            d.line((0, y + 1, 31, y + 1), fill=MADEIRA[1])
    else:
        raise ValueError(name)
    if name == "cerca":
        return np.array(im)  # emenda com a cerca vizinha: sem contorno nas pontas
    return outlined(im)


# Os estilos de 16px (gb16, nes16, dusk16) pintam a partir do banco data/tiles/gb16.json, no
# alfabeto do rig ('.' transparente, '1' '2' '3' tons da rampa, 'o' contorno), e o template
# exige o MESMO vocabulario de tiles em todo estilo. Entao cada tile do sertao tambem vira uma
# versao 16x16 derivada desta mesma arte, numa rampa que todo estilo tem.
RAMPS = {
    "terra": "terrain_path", "terra_alt": "terrain_path", "estrada": "skin_light", "pedra": "stone",
    "parede_madeira": "leather", "piso_madeira": "leather", "porta": "leather", "telhado": "skin_dark",
    "mandacaru": "terrain_bush", "arbusto_seco": "leather", "arvore_seca": "leather",
    "calango": "terrain_grass", "caveira": "skin_light", "poste": "leather", "placa": "terrain_bush",
    "cerca": "leather",
}
SOLID = {"pedra", "parede_madeira", "telhado", "mandacaru", "arbusto_seco", "arvore_seca", "poste",
         "placa", "cerca"}


def rig_rows(tile, decor):
    """32x32 RGBA -> 16 linhas de 16 caracteres no alfabeto do rig."""
    a = tile.astype(np.float64)
    alpha = a[..., 3].reshape(16, 2, 16, 2).mean((1, 3))
    rgb = a[..., :3].reshape(16, 2, 16, 2, 3)
    w = a[..., 3].reshape(16, 2, 16, 2, 1) / 255.0
    col = (rgb * w).sum((1, 3)) / np.maximum(w.sum((1, 3)), 1e-9)
    lum = col @ np.array([0.299, 0.587, 0.114])
    opaque = alpha >= 128 if decor else np.ones((16, 16), bool)
    dark = lum < 40
    vals = lum[opaque & ~dark]
    lo, hi = (np.percentile(vals, 33), np.percentile(vals, 70)) if len(vals) else (0, 0)
    rows = []
    for y in range(16):
        r = ""
        for x in range(16):
            if not opaque[y, x]:
                r += "."
            elif dark[y, x]:
                r += "o" if decor else "1"
            else:
                r += "1" if lum[y, x] < lo else ("2" if lum[y, x] < hi else "3")
        rows.append(r)
    return rows


CLARO = [(190, 150, 100), (214, 178, 124)]
BARRO = [(110, 52, 30), (156, 78, 44), (190, 104, 62), (214, 138, 90)]
CHITA = [(150, 30, 40), (196, 52, 56), (236, 196, 72), (60, 120, 180)]
TELA = (120, 200, 240)
FOGO = [(236, 120, 40), (252, 200, 80)]


def mesa(d):
    d.rectangle((2, 8, 29, 19), fill=MADEIRA[3])
    for y in (11, 15):
        d.line((3, y, 28, y), fill=MADEIRA[2])
    d.rectangle((2, 18, 29, 20), fill=MADEIRA[1])
    for x in (4, 25):
        d.rectangle((x, 21, x + 2, 29), fill=MADEIRA[2])


def furniture_tile(name):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "mesa":
        mesa(d)
        d.ellipse((17, 9, 23, 13), fill=BARRO[2])  # caneca
        d.rectangle((18, 8, 22, 9), fill=BARRO[3])
    elif name == "mesa_celular":
        mesa(d)
        d.rectangle((10, 9, 19, 16), fill=CINZA[0])  # o celular, aceso
        d.rectangle((11, 10, 18, 15), fill=TELA)
        d.line((12, 12, 16, 12), fill=OSSO[3])
        d.point((20, 9), fill=OSSO[3])  # vibrando
        d.point((21, 11), fill=OSSO[3])
    elif name == "cama_cima":
        d.rectangle((2, 1, 29, 7), fill=MADEIRA[2])
        d.line((2, 3, 29, 3), fill=MADEIRA[3])
        d.rectangle((3, 8, 28, 31), fill=OSSO[2])
        d.rectangle((6, 10, 25, 17), fill=OSSO[3])  # travesseiro
        d.line((6, 17, 25, 17), fill=OSSO[1])
        d.rectangle((3, 21, 28, 31), fill=CHITA[1])  # colcha de chita
        d.line((3, 21, 28, 21), fill=CHITA[0])
        for x in range(6, 28, 6):
            d.point((x, 25), fill=CHITA[2]); d.point((x + 3, 29), fill=CHITA[3])
    elif name == "cama_baixo":
        d.rectangle((3, 0, 28, 22), fill=CHITA[1])
        for y in (1, 9, 17):
            for x in range(6, 28, 6):
                d.point((x, y), fill=CHITA[2]); d.point((x + 3, y + 4), fill=CHITA[3])
        d.rectangle((2, 22, 29, 27), fill=MADEIRA[2])
        d.line((2, 24, 29, 24), fill=MADEIRA[3])
        for x in (3, 26):
            d.rectangle((x, 28, x + 2, 30), fill=MADEIRA[1])
    elif name == "fogao_lenha":
        d.rectangle((3, 9, 28, 29), fill=BARRO[2])
        for y in (14, 19, 24):
            d.line((3, y, 28, y), fill=BARRO[1])
        d.rectangle((3, 7, 28, 11), fill=CINZA[1])  # chapa
        d.ellipse((6, 7, 13, 10), fill=CINZA[0])
        d.ellipse((18, 7, 25, 10), fill=CINZA[0])
        d.rectangle((10, 17, 21, 26), fill=CINZA[0])  # boca
        d.rectangle((12, 22, 19, 25), fill=FOGO[0])
        d.point((14, 21), fill=FOGO[1]); d.point((17, 20), fill=FOGO[1]); d.point((15, 23), fill=FOGO[1])
        d.rectangle((24, 1, 27, 6), fill=CINZA[1])  # chamine
    elif name == "filtro_barro":
        d.ellipse((9, 3, 22, 15), fill=BARRO[2])
        d.rectangle((11, 2, 20, 4), fill=BARRO[3])
        d.ellipse((7, 13, 24, 28), fill=BARRO[2])
        d.line((10, 9, 13, 6), fill=BARRO[3])
        d.line((9, 20, 12, 17), fill=BARRO[3])
        d.rectangle((24, 21, 26, 22), fill=CINZA[1])  # torneira
        d.rectangle((8, 28, 23, 30), fill=MADEIRA[1])
    elif name == "estante":
        d.rectangle((3, 1, 28, 30), fill=MADEIRA[1])
        d.rectangle((5, 3, 26, 28), fill=MADEIRA[0])
        for y in (11, 20, 28):
            d.rectangle((3, y, 28, y + 1), fill=MADEIRA[3])
        for x, c in ((6, BARRO[2]), (12, CLARO[1]), (19, BARRO[3])):  # potes de rapadura
            d.rectangle((x, 5, x + 4, 10), fill=c)
            d.line((x, 5, x + 4, 5), fill=OSSO[2])
        for x, c in ((6, CHITA[3]), (9, CHITA[0]), (12, VERDE[2]), (15, CHITA[2])):  # livros
            d.rectangle((x, 13, x + 2, 19), fill=c)
        d.ellipse((19, 14, 25, 19), fill=OSSO[2])  # cuia
        d.rectangle((7, 22, 13, 27), fill=CLARO[0])
        d.rectangle((17, 23, 24, 27), fill=BARRO[1])
    elif name == "tapete":
        d.rectangle((3, 5, 28, 26), fill=CHITA[2])
        for y, c in ((8, CHITA[0]), (12, VERDE[2]), (16, CHITA[3]), (20, VERDE[2]), (23, CHITA[0])):
            d.line((4, y, 27, y), fill=c)
        for x in range(4, 28, 3):
            d.point((x, 4), fill=OSSO[2]); d.point((x, 27), fill=OSSO[2])
        return np.array(im)  # tapete e chao de pano: sem contorno
    else:
        raise ValueError(name)
    return outlined(im)


def life_tile(name):
    """O que deixa o sertao vivo: plantas, coisas de casa do lado de fora, Sao Joao."""
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "xique_xique":  # cacto baixo de bracos curvos, espalhado no chao
        for x0, y0, x1, y1 in ((12, 12, 17, 29), (4, 18, 9, 28), (21, 15, 26, 28), (8, 22, 13, 29)):
            d.rounded_rectangle((x0, y0, x1, y1), radius=2, fill=VERDE[1])
            d.line((x0 + 2, y0 + 1, x0 + 2, y1 - 1), fill=VERDE[2])
        for y in range(14, 28, 3):
            d.point((11, y), fill=OSSO[3]); d.point((18, y + 1), fill=OSSO[3])
    elif name == "palma":  # palma forrageira: raquetes ovais empilhadas
        for box in ((11, 18, 21, 30), (5, 9, 14, 21), (17, 7, 27, 19), (12, 2, 20, 11)):
            d.ellipse(box, fill=VERDE[2])
            d.ellipse((box[0] + 2, box[1] + 2, box[2] - 4, box[3] - 5), fill=VERDE[3])
        for x, y in ((8, 12), (22, 10), (15, 22), (16, 5)):
            d.point((x, y), fill=OSSO[3])
    elif name == "juazeiro":  # a arvore que fica verde na seca
        d.rectangle((14, 20, 17, 30), fill=SECO[1])
        d.ellipse((2, 2, 29, 23), fill=VERDE[1])
        d.ellipse((5, 3, 22, 17), fill=VERDE[2])
        for x, y in ((9, 7), (18, 6), (13, 12), (23, 11), (7, 14)):
            d.rectangle((x, y, x + 2, y + 1), fill=VERDE[3])
        d.point((20, 15), fill=(230, 196, 70)); d.point((10, 18), fill=(230, 196, 70))  # frutos
    elif name == "poco":  # poco/cacimba de pedra com balde
        d.ellipse((3, 14, 28, 30), fill=PEDRA[2])
        d.ellipse((7, 16, 24, 25), fill=(30, 40, 60))
        d.rectangle((4, 4, 6, 22), fill=MADEIRA[2]); d.rectangle((25, 4, 27, 22), fill=MADEIRA[2])
        d.rectangle((4, 3, 27, 5), fill=MADEIRA[1])
        d.line((16, 5, 16, 12), fill=CINZA[0])
        d.rectangle((13, 12, 19, 16), fill=CINZA[1])
    elif name == "fogueira":  # fogueira de Sao Joao
        d.line((6, 28, 26, 22), fill=MADEIRA[1], width=3)
        d.line((6, 22, 26, 28), fill=MADEIRA[2], width=3)
        d.polygon(((10, 24), (16, 6), (22, 24)), fill=FOGO[0])
        d.polygon(((13, 24), (16, 12), (19, 24)), fill=FOGO[1])
        d.point((12, 9), fill=FOGO[1]); d.point((21, 7), fill=FOGO[0])
    elif name == "bandeirinhas":  # cordao de bandeirinhas: emenda com o vizinho
        d.line((0, 5, 8, 7, 16, 8, 24, 7, 31, 5), fill=CINZA[0])
        cores = (CHITA[0], CHITA[2], CHITA[3], VERDE[2])
        for k, x in enumerate((2, 10, 18, 26)):
            y = 7 if k in (1, 2) else 6
            d.polygon(((x, y), (x + 5, y), (x + 2, y + 6)), fill=cores[k])
        return np.array(im)
    elif name == "varal":  # varal com roupa
        d.rectangle((2, 4, 3, 30), fill=MADEIRA[2]); d.rectangle((28, 4, 29, 30), fill=MADEIRA[2])
        d.line((3, 7, 28, 9), fill=CINZA[1])
        # camisa (T), calca com as duas pernas, pano de chita
        d.polygon(((5, 8), (13, 8), (14, 11), (12, 11), (12, 18), (6, 18), (6, 11), (4, 11)), fill=OSSO[3])
        d.polygon(((15, 9), (21, 9), (21, 20), (19, 20), (18, 13), (17, 20), (15, 20)), fill=(60, 90, 150))
        d.rectangle((23, 9, 27, 15), fill=CHITA[1])
        d.point((24, 11), fill=CHITA[2]); d.point((26, 13), fill=CHITA[2])
    elif name == "potes_barro":  # moringa e potes
        d.ellipse((3, 14, 15, 29), fill=BARRO[2]); d.rectangle((7, 11, 11, 15), fill=BARRO[2])
        d.ellipse((15, 18, 29, 30), fill=BARRO[1]); d.rectangle((19, 15, 25, 19), fill=BARRO[1])
        d.line((5, 18, 7, 16), fill=BARRO[3]); d.line((17, 22, 19, 20), fill=BARRO[3])
    elif name == "banco":  # banco de madeira
        d.rectangle((2, 13, 29, 18), fill=MADEIRA[3])
        d.line((2, 16, 29, 16), fill=MADEIRA[2])
        for x in (4, 25):
            d.rectangle((x, 19, x + 2, 27), fill=MADEIRA[1])
    elif name == "tambor":  # tambor azul de agua
        d.rectangle((7, 6, 24, 29), fill=(40, 90, 160))
        for y in (11, 18, 25):
            d.line((7, y, 24, y), fill=(26, 60, 110))
        d.ellipse((7, 3, 24, 9), fill=(70, 130, 200))
        d.line((10, 8, 10, 27), fill=(90, 150, 220))
    elif name == "roda_carroca":  # roda de carro de boi encostada
        d.ellipse((4, 4, 27, 27), outline=MADEIRA[1], width=3)
        d.ellipse((13, 13, 18, 18), fill=MADEIRA[2])
        for a in range(0, 360, 45):
            x = 15.5 + 10 * math.cos(math.radians(a)); y = 15.5 + 10 * math.sin(math.radians(a))
            d.line((15.5, 15.5, x, y), fill=MADEIRA[2])
    elif name == "pedras":
        d.ellipse((3, 16, 17, 29), fill=PEDRA[2]); d.ellipse((5, 17, 12, 22), fill=PEDRA[3])
        d.ellipse((14, 20, 28, 30), fill=PEDRA[1]); d.ellipse((16, 21, 22, 25), fill=PEDRA[2])
        d.ellipse((10, 10, 20, 20), fill=PEDRA[2]); d.ellipse((12, 11, 16, 14), fill=PEDRA[3])
    elif name == "capim":  # tufo de capim seco (da pra pisar)
        for x, h in ((8, 12), (11, 16), (14, 10), (17, 15), (20, 11), (23, 13)):
            d.line((x, 28, x + (1 if x % 2 else -1), 28 - h), fill=SECO[3])
            d.line((x + 1, 28, x + 2, 28 - h + 3), fill=SECO[2])
        return np.array(im)
    else:
        raise ValueError(name)
    return outlined(im)


VIDA = ["xique_xique", "palma", "juazeiro", "poco", "fogueira", "bandeirinhas", "varal", "potes_barro"]
VIDA2 = ["banco", "tambor", "roda_carroca", "pedras", "capim"]
RAMPS.update({"xique_xique": "terrain_bush", "palma": "terrain_bush", "juazeiro": "terrain_grass",
              "poco": "stone", "fogueira": "skin_dark", "bandeirinhas": "skin_light", "varal": "skin_light",
              "potes_barro": "skin_dark", "banco": "leather", "tambor": "terrain_water",
              "roda_carroca": "leather", "pedras": "stone", "capim": "terrain_path"})
SOLID |= {"xique_xique", "palma", "juazeiro", "poco", "fogueira", "varal", "potes_barro", "banco",
          "tambor", "roda_carroca", "pedras"}

MOVEIS = ["mesa", "mesa_celular", "cama_cima", "cama_baixo", "fogao_lenha", "filtro_barro", "estante", "tapete"]
RAMPS.update({"mesa": "leather", "mesa_celular": "leather", "cama_cima": "skin_dark",
              "cama_baixo": "skin_dark", "fogao_lenha": "skin_dark", "filtro_barro": "skin_dark",
              "estante": "leather", "tapete": "skin_dark"})
SOLID |= {"mesa", "mesa_celular", "cama_cima", "cama_baixo", "fogao_lenha", "filtro_barro", "estante"}


def main():
    root = Path(__file__).resolve().parent.parent
    out = root / "rpg-template" / "data" / "imports" / "tiles" / "lpc32" / "sertao.png"
    sheet = np.zeros((T * 5, T * COLS, 4), np.uint8)
    rig, cells = [], []
    for row, names, draw in ((0, GROUND, lambda n, i: ground_tile(n, np.random.default_rng(1000 + i))),
                             (1, DECOR, lambda n, i: decor_tile(n, np.random.default_rng(2000 + i))),
                             (2, MOVEIS, lambda n, i: furniture_tile(n)),
                             (3, VIDA, lambda n, i: life_tile(n)),
                             (4, VIDA2, lambda n, i: life_tile(n))):
        for i, name in enumerate(names):
            tile = draw(name, i)
            sheet[row * T:(row + 1) * T, i * T:(i + 1) * T] = tile
            entry = {"id": name, "ramp": RAMPS[name], "solid": name in SOLID}
            if row:
                entry["decor"] = True
            rig.append(dict(entry, rows=rig_rows(tile, row > 0)))
            cells.append({"id": name, "from": "sertao.png", "cell": [i, row], "solid": name in SOLID,
                          "decor": row > 0})
    Image.fromarray(sheet).save(out, optimize=False)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    write_rig_bank(root / "rpg-template" / "data" / "tiles" / "gb16.json", rig)
    write_lpc_bank(root / "rpg-template" / "data" / "tiles" / "lpc32.json", cells, sha)
    print(out)
    print("sha256", sha)


def write_lpc_bank(path, cells, sha):
    """Atualiza o sha256 de sertao.png e troca os tiles cortados dela no banco lpc32."""
    raw = path.read_text(encoding="utf-8")
    bank = json.loads(raw)
    assert json.dumps(bank, indent="\t", ensure_ascii=False) + "\n" == raw, "formato do lpc32.json mudou"
    for f in bank["files"]:
        if f["file"] == "sertao.png":
            f["sha256"] = sha
    bank["tiles"] = [t for t in bank["tiles"] if t.get("from") != "sertao.png"] + cells
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(bank, indent="\t", ensure_ascii=False) + "\n")
    print(path, f"({len(cells)} tiles do sertao)")


def write_rig_bank(path, rig):
    """Troca (ou acrescenta) os tiles do sertao no banco gb16, sem mexer nos outros."""
    raw = path.read_text(encoding="utf-8")
    bank = json.loads(raw)
    assert json.dumps(bank, indent="\t", ensure_ascii=False) + "\n" == raw, "formato do gb16.json mudou"
    ours = {t["id"] for t in rig}
    bank["tiles"] = [t for t in bank["tiles"] if t["id"] not in ours] + rig
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(bank, indent="\t", ensure_ascii=False) + "\n")
    print(path, f"(+{len(rig)} tiles 16px)")


if __name__ == "__main__":
    main()
