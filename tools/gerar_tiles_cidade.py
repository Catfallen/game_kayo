"""Desenha os tiles de Tres Lagoas (32x32) usados na fase 2.

Saida: rpg-template/data/imports/tiles/lpc32/cidade.png, uma folha de 8 colunas cortada pelo banco
data/tiles/lpc32.json, como a sertao.png do tools/gerar_tiles_sertao.py (daqui vem o contorno, a
conversao para 16px e o jeito de gravar os bancos). Deterministico.

Linhas: chao da cidade, praca e orla, barraca de terere e rodoviaria, aeroporto, e por ultimo os
veiculos grandes: o onibus (6x3 tiles) e o carro (2x1), desenhados inteiros e cortados em tiles.

Uso:  python -I tools/gerar_tiles_cidade.py   (depois o tools/gen_sprites.gd do template)
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from gerar_tiles_sertao import (CINZA, CONTORNO, MADEIRA, OSSO, T, VERDE, outlined, rig_rows,
                                speckle)

COLS = 8
FILE = "cidade.png"

ASFALTO = [(44, 46, 52), (62, 64, 72), (80, 82, 90), (100, 102, 110)]
CALCADA = [(150, 146, 140), (178, 174, 166), (200, 196, 188), (222, 218, 210)]
ORLA = [(168, 92, 70), (196, 120, 92), (216, 150, 120), (232, 184, 156)]  # calcadao de bloquete
REBOCO = [(196, 170, 120), (222, 200, 150), (238, 222, 180), (248, 238, 210)]
CERAMICA = [(176, 178, 184), (204, 206, 212), (226, 228, 232), (244, 245, 248)]
CEU = [(120, 180, 230), (160, 206, 240), (200, 228, 248)]
AMARELO = [(196, 140, 20), (236, 188, 40), (252, 222, 90)]
ROSA = [(176, 60, 120), (220, 100, 160), (244, 156, 200)]
AZUL = [(30, 70, 140), (50, 110, 190), (100, 160, 230)]
VERMELHO = [(150, 30, 30), (200, 50, 50), (236, 100, 90)]
BRANCO = (246, 246, 240)

GROUND = ["asfalto", "asfalto_faixa", "calcada", "calcadao", "parede_reboco", "piso_ceramica",
          "vidro", "porta_vidro"]
PRACA = ["ipe_amarelo", "ipe_rosa", "coqueiro", "poste_luz", "banco_praca", "lixeira", "flores",
         "placa_tl"]
RUA = ["barraca_esq", "barraca_dir", "placa_rodoviaria", "orelhao", "sorveteria"]
AERO = ["balcao", "cadeiras", "painel_voos", "vaso_planta", "portao", "mala", "bebedouro",
        "placa_aviao"]
# Veiculos: cada um e uma figura so, cortada em pedacos de um tile. onibus_<linha><coluna>.
ONIBUS_W, ONIBUS_H = 6, 3
ONIBUS = [[f"onibus_{y}{x}" for x in range(ONIBUS_W)] for y in range(ONIBUS_H)]
CARRO = ["carro_esq", "carro_dir"]
VEICULOS = (ONIBUS[0] + CARRO, ONIBUS[1], ONIBUS[2])

RAMPS = {
    "asfalto": "stone", "asfalto_faixa": "stone", "calcada": "stone", "calcadao": "skin_dark",
    "parede_reboco": "skin_light", "piso_ceramica": "stone", "vidro": "terrain_water",
    "porta_vidro": "terrain_water",
    "ipe_amarelo": "skin_light", "ipe_rosa": "skin_dark", "coqueiro": "terrain_bush",
    "poste_luz": "stone", "banco_praca": "leather", "lixeira": "terrain_bush", "flores": "terrain_grass",
    "placa_tl": "terrain_bush",
    "barraca_esq": "skin_dark", "barraca_dir": "skin_dark", "placa_rodoviaria": "terrain_water",
    "orelhao": "terrain_water", "sorveteria": "skin_light",
    "balcao": "leather", "cadeiras": "terrain_water", "painel_voos": "stone", "vaso_planta": "terrain_bush",
    "portao": "terrain_water", "mala": "skin_dark", "bebedouro": "stone", "placa_aviao": "terrain_water",
}
RAMPS.update({n: "terrain_water" for row in ONIBUS for n in row})
RAMPS.update({n: "skin_dark" for n in CARRO})
# so o que da para pisar fica de fora: chao, porta de vidro e as flores
SOLID = ({"parede_reboco", "vidro"} | (set(PRACA) | set(RUA) | set(AERO)) - {"flores"}
         | {n for row in ONIBUS for n in row} | set(CARRO))


def opaque(img):
    out = np.zeros((T, T, 4), np.uint8)
    out[..., :3] = img
    out[..., 3] = 255
    return out


def ground_tile(name, rng):
    if name == "asfalto":
        img = speckle(rng, ASFALTO, 1, 0.12)
    elif name == "asfalto_faixa":  # faixa amarela tracejada no meio da pista, emenda com a vizinha
        img = speckle(rng, ASFALTO, 1, 0.12)
        img[15:17, 2:14] = AMARELO[1]
        img[15:17, 18:30] = AMARELO[1]
    elif name == "calcada":
        img = speckle(rng, CALCADA, 2, 0.08)
        for k in (0, 16):
            img[k] = CALCADA[0]
            img[:, k] = CALCADA[0]
    elif name == "calcadao":  # bloquete em espinha de peixe, o calcadao da Lagoa Maior
        img = speckle(rng, ORLA, 2, 0.06)
        for y in range(0, T, 8):
            for x in range(0, T, 8):
                if ((x + y) // 8) % 2:
                    img[y:y + 8, x] = ORLA[0]
                    img[y + 3, x:x + 8] = ORLA[0]
                else:
                    img[y, x:x + 8] = ORLA[0]
                    img[y:y + 8, x + 3] = ORLA[0]
    elif name == "parede_reboco":
        img = speckle(rng, REBOCO, 2, 0.06)
        img[26:] = REBOCO[0]  # rodape
        img[26] = REBOCO[3]
    elif name == "piso_ceramica":
        img = speckle(rng, CERAMICA, 2, 0.04)
        for k in (0, 16):
            img[k] = CERAMICA[0]
            img[:, k] = CERAMICA[0]
        img[3:5, 3:5] = CERAMICA[3]
        img[19:21, 19:21] = CERAMICA[3]
    elif name in ("vidro", "porta_vidro"):  # janelao do aeroporto: ceu e pista la fora
        img = np.zeros((T, T, 3), np.uint8)
        for y in range(T):
            img[y] = CEU[min(2, y // 10)]
        img[22:] = (96, 140, 90)
        img[25:27] = (70, 70, 76)
        img[:, :2] = CINZA[1]
        img[:2] = CINZA[1]
        if name == "vidro":
            img[:, 15:17] = CINZA[1]
            img[5:9, 6:8] = BRANCO  # reflexo
        else:
            img[:, 15:17] = CINZA[0]
            img[14:18, 11:14] = CINZA[0]
            img[14:18, 18:21] = CINZA[0]
            img[28:] = CERAMICA[1]  # o chao entra pela porta: e o caminho
    else:
        raise ValueError(name)
    return opaque(img)


def copa(d, ramp, rng, box):
    x0, y0, x1, y1 = box
    d.ellipse(box, fill=ramp[0])
    d.ellipse((x0 + 2, y0 + 1, x1 - 3, y1 - 4), fill=ramp[1])
    for _ in range(18):
        x, y = int(rng.integers(x0 + 3, x1 - 3)), int(rng.integers(y0 + 2, y1 - 4))
        d.rectangle((x, y, x + 1, y + 1), fill=ramp[2])


def praca_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name in ("ipe_amarelo", "ipe_rosa"):  # o ipe florido de setembro
        d.rectangle((14, 18, 17, 30), fill=MADEIRA[1])
        d.line((15, 22, 9, 15), fill=MADEIRA[1], width=2)
        d.line((16, 21, 23, 14), fill=MADEIRA[1], width=2)
        copa(d, AMARELO if name == "ipe_amarelo" else ROSA, rng, (1, 1, 30, 22))
    elif name == "coqueiro":
        d.line((18, 30, 15, 9), fill=MADEIRA[2], width=3)
        for y in range(12, 30, 4):
            d.line((14, y, 18, y), fill=MADEIRA[1])
        for x1, y1 in ((2, 10), (6, 3), (15, 1), (25, 3), (30, 11), (4, 15), (28, 16)):
            d.line((15, 8, x1, y1), fill=VERDE[2], width=2)
            d.line((15, 9, (15 + x1) // 2, (8 + y1) // 2 + 2), fill=VERDE[1])
        d.ellipse((12, 7, 16, 11), fill=MADEIRA[1])
        d.ellipse((15, 8, 19, 12), fill=MADEIRA[0])
    elif name == "poste_luz":
        d.rectangle((15, 6, 16, 30), fill=CINZA[1])
        d.line((16, 6, 22, 4), fill=CINZA[1], width=2)
        d.rectangle((20, 3, 26, 6), fill=CINZA[0])
        d.rectangle((21, 6, 25, 7), fill=AMARELO[2])
        d.rectangle((12, 28, 19, 30), fill=CINZA[0])
    elif name == "banco_praca":  # banco de praca de ripas verdes com pe de ferro
        d.rectangle((2, 8, 29, 10), fill=VERDE[2])
        d.rectangle((2, 12, 29, 14), fill=VERDE[2])
        d.rectangle((2, 17, 29, 20), fill=VERDE[3])
        d.line((2, 20, 29, 20), fill=VERDE[1])
        for x in (4, 26):
            d.rectangle((x, 8, x + 1, 28), fill=CINZA[0])
    elif name == "lixeira":
        d.rectangle((10, 10, 21, 28), fill=VERDE[2])
        d.rectangle((9, 8, 22, 11), fill=VERDE[1])
        d.line((13, 13, 13, 26), fill=VERDE[3])
        d.line((18, 13, 18, 26), fill=VERDE[3])
    elif name == "flores":  # canteiro baixo, da para pisar
        for x, y, c in ((5, 20, ROSA[1]), (11, 25, AMARELO[1]), (17, 19, VERMELHO[2]), (23, 24, ROSA[2]),
                        (27, 18, AMARELO[2]), (8, 13, VERMELHO[1]), (20, 12, AMARELO[1])):
            d.line((x + 1, y + 2, x + 1, y + 6), fill=VERDE[1])
            d.ellipse((x - 1, y - 1, x + 3, y + 3), fill=c)
            d.point((x + 1, y + 1), fill=AMARELO[2])
        return np.array(im)
    elif name == "placa_tl":  # "TRES LAGOAS" em letreiro de praca
        d.rectangle((14, 18, 17, 30), fill=CINZA[1])
        d.rectangle((1, 5, 30, 19), fill=AZUL[1])
        d.rectangle((2, 6, 29, 18), outline=BRANCO)
        for k, x in enumerate(range(5, 27, 4)):  # letras de mentira, duas linhas
            d.rectangle((x, 9, x + 2, 11), fill=BRANCO)
            if k % 2 == 0:
                d.rectangle((x + 1, 14, x + 3, 15), fill=BRANCO)
    else:
        raise ValueError(name)
    return outlined(im)


def toldo(d, x0, x1):
    for k, x in enumerate(range(x0, x1, 4)):
        d.rectangle((x, 2, min(x + 3, x1), 9), fill=VERMELHO[1] if k % 2 == 0 else BRANCO)
    d.line((x0, 10, x1, 10), fill=VERMELHO[0])


def rua_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "barraca_esq":  # barraca de terere: toldo listrado, guampas e garrafa termica
        toldo(d, 0, 31)
        d.rectangle((1, 10, 2, 29), fill=MADEIRA[1])
        d.rectangle((0, 18, 31, 29), fill=MADEIRA[2])
        d.line((0, 18, 31, 18), fill=MADEIRA[3])
        for x in (5, 12):  # guampas de chifre com bomba
            d.polygon(((x, 12), (x + 5, 12), (x + 4, 17), (x + 1, 17)), fill=OSSO[1])
            d.line((x + 3, 9, x + 3, 13), fill=(200, 200, 210))
        d.rectangle((19, 10, 26, 17), fill=VERMELHO[1])  # garrafa termica (cooler)
        d.rectangle((19, 10, 26, 11), fill=BRANCO)
        d.rectangle((26, 12, 28, 13), fill=CINZA[1])
        return outlined_open(im, right=True)
    elif name == "barraca_dir":
        toldo(d, 0, 31)
        d.rectangle((29, 10, 30, 29), fill=MADEIRA[1])
        d.rectangle((0, 18, 31, 29), fill=MADEIRA[2])
        d.line((0, 18, 31, 18), fill=MADEIRA[3])
        d.rectangle((4, 20, 26, 27), fill=VERDE[1])  # plaquinha TERERE
        for x in range(6, 25, 4):
            d.rectangle((x, 22, x + 2, 25), fill=BRANCO)
        for x in (6, 14, 21):  # limoes e hortela
            d.ellipse((x, 13, x + 4, 17), fill=(140, 200, 60))
        return outlined_open(im, left=True)
    elif name == "placa_rodoviaria":
        d.rectangle((14, 18, 17, 30), fill=CINZA[1])
        d.rectangle((2, 4, 29, 18), fill=AZUL[1])
        d.rectangle((6, 7, 12, 13), fill=BRANCO)  # icone de onibus
        d.rectangle((7, 8, 11, 10), fill=AZUL[1])
        d.line((15, 9, 26, 9), fill=BRANCO)
        d.line((15, 13, 23, 13), fill=BRANCO)
    elif name == "orelhao":  # o orelhao, que toda cidade ainda tem
        d.rectangle((15, 16, 16, 30), fill=CINZA[1])
        d.ellipse((6, 2, 25, 22), fill=AZUL[1])
        d.ellipse((9, 6, 22, 22), fill=AZUL[0])
        d.rectangle((13, 10, 18, 17), fill=CINZA[1])
    elif name == "sorveteria":  # carrinho de picole
        d.rectangle((4, 10, 27, 24), fill=BRANCO)
        d.rectangle((4, 10, 27, 13), fill=ROSA[1])
        d.rectangle((9, 15, 22, 21), fill=AZUL[2])
        d.ellipse((14, 3, 19, 9), fill=ROSA[2])
        d.line((16, 9, 16, 11), fill=MADEIRA[3])
        for x in (6, 22):
            d.ellipse((x, 23, x + 5, 28), fill=CINZA[0])
    else:
        raise ValueError(name)
    return outlined(im)


def outlined_open(im, left=False, right=False):
    """Contorno, menos no lado que emenda com a outra metade (barraca e onibus tem dois tiles)."""
    a = outlined(im)
    raw = np.array(im)
    if right:
        a[:, -1] = raw[:, -1]
    if left:
        a[:, 0] = raw[:, 0]
    return a


def aero_tile(name, rng):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if name == "balcao":  # balcao do check-in, emenda com o vizinho
        d.rectangle((0, 10, 31, 29), fill=MADEIRA[2])
        d.rectangle((0, 8, 31, 11), fill=CERAMICA[0])
        d.line((0, 18, 31, 18), fill=MADEIRA[1])
        d.rectangle((12, 4, 20, 9), fill=CINZA[0])  # monitor
        d.rectangle((13, 5, 19, 8), fill=CEU[1])
        return np.array(outlined_open(im, left=True, right=True))
    elif name == "cadeiras":  # longarina de cadeiras azuis
        for x in (1, 11, 21):
            d.rectangle((x, 8, x + 8, 15), fill=AZUL[1])
            d.rectangle((x, 16, x + 8, 20), fill=AZUL[2])
        d.rectangle((0, 21, 31, 22), fill=CINZA[1])
        for x in (3, 28):
            d.rectangle((x, 22, x + 1, 29), fill=CINZA[1])
    elif name == "painel_voos":  # o painel de partidas
        d.rectangle((1, 2, 30, 20), fill=(20, 22, 30))
        for y in (5, 9, 13, 17):
            d.line((4, y, 18, y), fill=AMARELO[2])
            d.line((21, y, 27, y), fill=(120, 230, 120) if y != 5 else VERMELHO[2])
        d.rectangle((14, 21, 17, 30), fill=CINZA[1])
    elif name == "vaso_planta":
        d.polygon(((9, 20), (22, 20), (20, 30), (11, 30)), fill=(150, 90, 60))
        for x1, y1 in ((4, 6), (10, 2), (16, 1), (22, 3), (28, 8), (6, 14), (26, 14)):
            d.line((15, 21, x1, y1), fill=VERDE[2], width=2)
    elif name == "portao":  # placa do portao de embarque, pendurada
        d.line((8, 0, 8, 5), fill=CINZA[1])
        d.line((23, 0, 23, 5), fill=CINZA[1])
        d.rectangle((2, 5, 29, 17), fill=AMARELO[1])
        d.text((6, 6), "EMB", fill=(20, 20, 20))
        d.rectangle((24, 7, 26, 15), fill=(20, 20, 20))  # o 1 do portao 1
        d.rectangle((10, 19, 21, 30), fill=CINZA[1])  # leitor de cartao
        d.rectangle((12, 21, 19, 25), fill=(120, 230, 120))
    elif name == "mala":  # mala de rodinha esquecida no saguao
        d.rounded_rectangle((9, 12, 22, 29), radius=2, fill=ROSA[1])
        d.line((12, 12, 12, 6), fill=CINZA[1])
        d.line((19, 12, 19, 6), fill=CINZA[1])
        d.line((12, 6, 19, 6), fill=CINZA[1])
        d.line((9, 20, 22, 20), fill=ROSA[0])
    elif name == "bebedouro":
        d.rectangle((9, 8, 22, 29), fill=CERAMICA[1])
        d.rectangle((9, 8, 22, 12), fill=CINZA[1])
        d.ellipse((13, 9, 18, 11), fill=AZUL[2])
    elif name == "placa_aviao":  # placa de saguao com o aviaozinho
        d.line((15, 0, 15, 6), fill=CINZA[1])
        d.rectangle((2, 6, 29, 20), fill=AZUL[0])
        d.polygon(((6, 13), (18, 12), (22, 9), (23, 12), (26, 13), (23, 14), (22, 17), (18, 14)), fill=BRANCO)
    else:
        raise ValueError(name)
    return outlined(im)


def onibus():
    """O onibus que trouxe o Kayo do Maranhao, de lado, com a frente (e a porta) para a direita."""
    im = Image.new("RGBA", (ONIBUS_W * T, ONIBUS_H * T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = ONIBUS_W * T
    d.rounded_rectangle((2, 6, w - 3, 84), radius=6, fill=BRANCO)
    d.rectangle((4, 6, w - 6, 12), fill=CERAMICA[0])  # teto
    for x in range(10, 150, 24):  # janelas dos passageiros
        d.rectangle((x, 18, x + 19, 44), fill=AZUL[2])
        d.line((x, 18, x + 19, 18), fill=CEU[2])
        d.line((x + 2, 21, x + 6, 21), fill=BRANCO)
    d.rectangle((w - 22, 16, w - 5, 50), fill=AZUL[0])  # para-brisa
    d.line((w - 20, 19, w - 14, 19), fill=CEU[2])
    d.rectangle((150, 18, 166, 82), fill=AZUL[0])  # porta
    d.rectangle((152, 20, 157, 54), fill=AZUL[2])
    d.rectangle((159, 20, 164, 54), fill=AZUL[2])
    d.rectangle((2, 52, 147, 66), fill=AZUL[1])  # faixa com o destino
    d.text((10, 53), "MARANHAO > TRES LAGOAS", fill=BRANCO)
    d.rectangle((168, 52, w - 3, 66), fill=AZUL[1])
    d.rectangle((w - 7, 68, w - 3, 74), fill=AMARELO[2])  # farol
    d.rectangle((2, 74, w - 3, 78), fill=CINZA[1])  # para-choque
    for cx in (34, 140):
        d.ellipse((cx - 13, 70, cx + 13, 95), fill=CINZA[0])
        d.ellipse((cx - 6, 77, cx + 6, 88), fill=CINZA[1])
    return outlined(im)


def carro():
    """Fusca vermelho estacionado, de lado."""
    im = Image.new("RGBA", (2 * T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((14, 1, 50, 30), fill=VERMELHO[1])
    d.rounded_rectangle((2, 13, 61, 26), radius=5, fill=VERMELHO[1])
    d.rectangle((20, 6, 30, 14), fill=CEU[1])
    d.rectangle((33, 6, 43, 14), fill=CEU[1])
    d.line((3, 19, 60, 19), fill=VERMELHO[0])
    d.rectangle((57, 15, 60, 18), fill=AMARELO[2])
    for cx in (14, 49):
        d.ellipse((cx - 6, 20, cx + 6, 31), fill=CINZA[0])
        d.ellipse((cx - 2, 24, cx + 2, 28), fill=CINZA[1])
    return outlined(im)


_FIGURAS = {}


def veiculo_tile(name, rng):
    """Um pedaco de um tile do onibus ou do carro."""
    if not _FIGURAS:
        _FIGURAS["onibus"], _FIGURAS["carro"] = onibus(), carro()
    if name in CARRO:
        fig, y, x = _FIGURAS["carro"], 0, CARRO.index(name)
    else:
        fig, y, x = _FIGURAS["onibus"], int(name[-2]), int(name[-1])
    return fig[y * T:(y + 1) * T, x * T:(x + 1) * T]


def main():
    root = Path(__file__).resolve().parent.parent
    out = root / "rpg-template" / "data" / "imports" / "tiles" / "lpc32" / FILE
    rows = ((0, GROUND, ground_tile), (1, PRACA, praca_tile), (2, RUA, rua_tile), (3, AERO, aero_tile),
            (4, VEICULOS[0], veiculo_tile), (5, VEICULOS[1], veiculo_tile), (6, VEICULOS[2], veiculo_tile))
    sheet = np.zeros((T * len(rows), T * COLS, 4), np.uint8)
    rig, cells = [], []
    for row, names, draw in rows:
        for i, name in enumerate(names):
            tile = np.asarray(draw(name, np.random.default_rng(3000 + row * 100 + i)))
            sheet[row * T:(row + 1) * T, i * T:(i + 1) * T] = tile
            # um pedaco de veiculo sem nenhum furo e chao (o template recusa decoracao opaca)
            decor = row > 0 and not (row >= 4 and tile[..., 3].min() == 255)
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
             "notes": "Desenhado por game_kayo/tools/gerar_tiles_cidade.py; os tiles de Tres Lagoas da fase 2."}
    old = {t["id"] for t in lpc["tiles"] if t.get("from") == FILE}
    lpc["files"] = [f for f in lpc["files"] if f["file"] != FILE] + [entry]
    lpc["tiles"] = [t for t in lpc["tiles"] if t.get("from") != FILE] + cells
    _save(tiles_dir / "lpc32.json", lpc)
    gb = _load(tiles_dir / "gb16.json")
    ours = {t["id"] for t in rig} | old  # o que saiu da folha sai do banco de 16px tambem
    gb["tiles"] = [t for t in gb["tiles"] if t["id"] not in ours] + rig
    _save(tiles_dir / "gb16.json", gb)
    print(f"bancos: +{len(cells)} tiles da cidade")


if __name__ == "__main__":
    main()
