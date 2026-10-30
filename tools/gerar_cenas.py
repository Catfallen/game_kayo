"""Desenha as cenas animadas que aparecem acima da caixa de dialogo (DialogScene do template).

Cada cena e uma tira PNG de quadros 128x72 lado a lado, mais um <cena>.json com quantos quadros sao,
quanto tempo cada um fica (em quadros de fisica, 60 por segundo) e de onde a animacao volta a repetir.
Os personagens sao os proprios sprites do jogo (assets/sprites/*.png, gerados de foto unica por
tools/gerar_sprites.py), em tamanho natural: na tela a cena aparece com o dobro do tamanho do mapa.

Saida: rpg-template/assets/kayo/cenas/. Deterministico.  Uso:  python -I tools/gerar_cenas.py
"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 128, 72
CHAO = 70  # a linha dos pes
ROOT = Path(__file__).resolve().parent.parent
SPRITES = ROOT / "assets" / "sprites"
OUT = ROOT / "rpg-template" / "assets" / "kayo" / "cenas"

BAIXO, ESQ, DIR, CIMA = 0, 1, 2, 3
PELE = (238, 190, 150, 255)
PELE_ISA = (232, 196, 170, 255)
LAGRIMA = (120, 190, 255, 255)
CORACAO = [(200, 30, 60, 255), (250, 80, 110, 255), (255, 170, 190, 255)]

_sheets = {}


def sprite(nome, direcao, quadro=0):
    if nome not in _sheets:
        _sheets[nome] = Image.open(SPRITES / f"{nome}.png").convert("RGBA")
    return _sheets[nome].crop((quadro * 64, direcao * 64, quadro * 64 + 64, direcao * 64 + 64))


def colar(img, spr, x, chao=CHAO, dy=0):
    """Poe o sprite com os pes (32, 63 da celula) em (x, chao)."""
    img.alpha_composite(spr, (int(x) - 32, chao - 63 + dy))


def lados(spr, y):
    """Primeira e ultima coluna opaca do sprite na linha y da celula."""
    cols = [x for x in range(64) if spr.getpixel((x, y))[3] > 0]
    return (cols[0], cols[-1]) if cols else (32, 32)


def topo(spr):
    for y in range(64):
        if any(spr.getpixel((x, y))[3] for x in range(64)):
            return y
    return 0


def coracao(d, x, y, cor=0, grande=False):
    c = CORACAO[cor]
    if grande:
        pts = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    else:
        pts = ["X.X", "XXX", ".X."]
    for j, row in enumerate(pts):
        for i, ch in enumerate(row):
            if ch == "X":
                d.point((x + i, y + j), fill=c)
    if grande:
        d.point((x + 1, y + 1), fill=CORACAO[2])


def ceu(img, cores):
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        k = min(len(cores) - 2, int(t * (len(cores) - 1)))
        f = t * (len(cores) - 1) - k
        a, b = cores[k], cores[k + 1]
        d.line((0, y, W, y), fill=tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3)) + (255,))
    return d


def fundo_rodoviaria():
    img = Image.new("RGBA", (W, H))
    d = ceu(img, [(150, 200, 240), (200, 228, 248)])
    d.rectangle((0, 18, W, 58), fill=(238, 222, 180, 255))  # predio da rodoviaria
    d.rectangle((0, 18, W, 21), fill=(200, 170, 120, 255))
    d.rectangle((24, 24, 104, 34), fill=(50, 110, 190, 255))
    d.text((34, 24), "RODOVIARIA", fill=(246, 246, 240, 255))
    for x in (6, 104):
        d.rectangle((x, 38, x + 18, 58), fill=(120, 180, 230, 255))
        d.line((x + 9, 38, x + 9, 58), fill=(86, 86, 94, 255))
    d.rectangle((0, 58, W, H), fill=(200, 196, 188, 255))  # calcada
    for x in range(0, W, 16):
        d.line((x, 58, x, H), fill=(150, 146, 140, 255))
    return img


def fundo_lagoa():
    img = Image.new("RGBA", (W, H))
    d = ceu(img, [(130, 190, 240), (196, 226, 248)])
    d.rectangle((0, 30, W, 50), fill=(60, 130, 180, 255))  # a Lagoa Maior
    for k in range(14):
        x, y = (k * 37) % W, 33 + (k * 7) % 15
        d.line((x, y, x + 4, y), fill=(160, 210, 240, 255))
    for x in range(0, W, 12):  # outra margem
        d.ellipse((x - 4, 22, x + 10, 34), fill=(60, 110, 60, 255))
    d.ellipse((20, 18, 36, 32), fill=(236, 188, 40, 255))  # ipe amarelo la longe
    d.ellipse((90, 19, 104, 31), fill=(220, 100, 160, 255))  # ipe rosa
    d.rectangle((0, 50, W, 54), fill=(86, 126, 66, 255))  # grama da margem
    d.rectangle((0, 54, W, H), fill=(216, 150, 120, 255))  # calcadao
    for x in range(0, W, 8):
        d.line((x, 54, x, H), fill=(168, 92, 70, 255))
    return img


def fundo_aeroporto():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(214, 216, 222, 255))
    d.rectangle((4, 4, W - 5, 46), fill=(150, 200, 240, 255))  # o janelao
    d.rectangle((4, 34, W - 5, 46), fill=(110, 150, 100, 255))
    d.rectangle((4, 38, W - 5, 41), fill=(80, 80, 86, 255))
    aviao(d, 70, 31, 1.0)
    for x in range(4, W, 30):
        d.line((x, 4, x, 46), fill=(120, 124, 132, 255), width=2)
    d.rectangle((0, 46, W, H), fill=(226, 228, 232, 255))  # piso
    for x in range(0, W, 16):
        d.line((x, 46, x - 10, H), fill=(196, 198, 204, 255))
    d.rectangle((0, 2, 20, 10), fill=(20, 22, 30, 255))  # painel de voos
    d.line((3, 5, 17, 5), fill=(252, 222, 90, 255))
    d.line((3, 8, 13, 8), fill=(252, 222, 90, 255))
    return img


def aviao(d, x, y, s):
    """Aviao de perfil apontando para a esquerda, com o nariz em (x, y); s e a escala."""
    def p(px, py):
        return (x + px * s, y + py * s)
    branco, azul, cinza = (246, 246, 240, 255), (50, 110, 190, 255), (120, 124, 132, 255)
    d.polygon([p(0, 0), p(4, -3), p(30, -3), p(36, -11), p(40, -11), p(38, -3), p(40, 0), p(4, 2)], fill=branco)
    d.polygon([p(14, 0), p(24, 0), p(30, 6), p(26, 6)], fill=cinza)  # asa
    d.line([p(4, -1), p(36, -1)], fill=azul)
    for k in range(6, 30, 4):
        d.point(p(k, -2), fill=azul)


def abraco_quadros(fundo, corre=False, lagrimas=False, coracoes=True, n_squeeze=8, isa_spr="isa_casual",
                   extra=None):
    """Os dois se aproximam e se abracam; depois o aperto pulsa (com coracao ou com lagrima).

    Em close: os personagens sao montados numa camada de meia resolucao, da cabeca a cintura, e
    ampliados 2x por cima do fundo - entram pelos lados da tela e se encontram no meio."""
    quadros = []
    lw, lh = W // 2, H // 2
    chao = 60  # na camada: os pes ficam bem abaixo da borda, so aparece da cintura para cima
    centro = lw // 2
    perto = 3  # distancia de cada um ao centro no abraco
    longe = 26

    def compor(camada):
        img = fundo.copy()
        img.alpha_composite(camada.resize((W, H), Image.NEAREST))
        return img

    passos = 6
    for i in range(passos):
        t = (i + 1) / passos
        dist = longe + (perto - longe) * t
        img = Image.new("RGBA", (lw, lh))
        colar(img, sprite("kayo", DIR, 1 + (i * (2 if corre else 1)) % 8), centro - dist, chao)
        colar(img, sprite(isa_spr, ESQ, 1 + (i * 2 + 3) % 8), centro + dist, chao)
        out = compor(img)
        if extra:
            extra(out, i)
        quadros.append(out)
    for k in range(n_squeeze + 1):
        img = Image.new("RGBA", (lw, lh))
        aperto = 0 if k == 0 else (1 if (k % 4) in (1, 2) else 0)
        kayo = sprite("kayo", DIR, 0)
        isa = sprite(isa_spr, ESQ, 0)
        xk, xi = centro - perto + aperto, centro + perto - aperto
        colar(img, kayo, xk, chao, dy=-aperto)
        colar(img, isa, xi, chao, dy=-aperto)
        d = ImageDraw.Draw(img)
        tk, ti = topo(kayo), topo(isa)
        oy_k = chao - 63 - aperto
        # so as maos aparecem: a dela nas costas dele, a dele nas costas dela
        yb = oy_k + tk + 21
        ek = lados(kayo, tk + 21)[0] + int(xk) - 32
        d.rectangle((ek - 2, yb, ek, yb + 3), fill=PELE_ISA)
        d.point((ek - 2, yb + 4), fill=PELE_ISA)
        bi = lados(isa, ti + 18)[1] + int(xi) - 32
        yh = oy_k + ti + 17
        d.rectangle((bi, yh, bi + 2, yh + 3), fill=PELE)
        d.point((bi + 2, yh + 4), fill=PELE)
        topo_y = min(oy_k + tk, oy_k + ti)
        if coracoes and k > 0:
            for j, (bx, fase) in enumerate(((centro - 13, 0), (centro + 10, 3), (centro - 9, 5))):
                sobe = ((k + fase) % 8) * 2
                if sobe < 14:
                    coracao(d, bx, topo_y + 16 - sobe, cor=j % 2)
            if k % 4 in (1, 2):
                coracao(d, centro - 3, topo_y - 7, grande=True)
        if lagrimas and k > 0:
            for j, ox in enumerate((int(xk) - 32 + lados(kayo, tk + 12)[1] - 1,
                                   int(xi) - 32 + lados(isa, ti + 12)[0] + 1)):
                cai = ((k * 2 + j * 3) % 8)
                ly = oy_k + (tk if j == 0 else ti) + 13 + cai
                d.rectangle((ox, ly, ox + 1, ly + 1), fill=LAGRIMA)
            if k % 4 in (1, 2):
                coracao(d, centro - 3, topo_y - 7, cor=0, grande=True)
        out = compor(img)
        if extra:
            extra(out, passos + k)
        quadros.append(out)
    return quadros


def terere_quadros():
    """Em close, como os abracos: camada de meia resolucao ampliada 2x por cima da Lagoa."""
    fundo = fundo_lagoa()
    lw, lh = W // 2, H // 2
    chao = 56
    centro = lw // 2
    xk, xi = centro - 9, centro + 9
    kayo, isa = sprite("kayo", DIR, 0), sprite("isa_casual", ESQ, 0)
    tk, ti = topo(kayo), topo(isa)
    boca_k = (xk - 32 + lados(kayo, tk + 13)[1] + 1, chao - 63 + tk + 14)
    boca_i = (xi - 32 + lados(isa, ti + 13)[0] - 1, chao - 63 + ti + 14)
    peito_k = (boca_k[0] + 2, boca_k[1] + 12)
    peito_i = (boca_i[0] - 2, boca_i[1] + 12)
    # caminho da guampa: no peito do Kayo, na boca dele, de volta, ate a Isa, na boca dela, de volta
    caminho = [peito_k, peito_k, boca_k, boca_k, boca_k, peito_k,
               ((peito_k[0] + peito_i[0]) // 2, peito_k[1] - 2), peito_i, peito_i, boca_i, boca_i, boca_i, peito_i,
               ((peito_k[0] + peito_i[0]) // 2, peito_k[1] - 2)]
    quadros = []
    for k, (gx, gy) in enumerate(caminho):
        img = Image.new("RGBA", (lw, lh))
        colar(img, kayo, xk, chao)
        colar(img, isa, xi, chao)
        d = ImageDraw.Draw(img)
        # a guampa (copo de chifre) e a bomba de metal
        d.polygon(((gx - 3, gy - 2), (gx + 3, gy - 2), (gx + 2, gy + 5), (gx - 2, gy + 5)), fill=(226, 218, 200, 255))
        d.line((gx - 3, gy - 2, gx + 3, gy - 2), fill=(120, 110, 96, 255))
        d.line((gx, gy - 6, gx, gy - 1), fill=(200, 200, 210, 255))
        d.point((gx - 1, gy - 1), fill=(90, 160, 60, 255))  # erva
        d.point((gx + 1, gy - 1), fill=(90, 160, 60, 255))
        if (gx, gy) in (boca_k, boca_i):  # gelado!
            for j in range(3):
                d.point((gx + (-6 if (gx, gy) == boca_i else 6) + j, gy - 6 - (k + j) % 3), fill=(200, 236, 255, 255))
        if k in (4, 11):
            coracao(d, centro - 1, 4 + (k % 3))
        out = fundo.copy()
        out.alpha_composite(img.resize((W, H), Image.NEAREST))
        quadros.append(out)
    return quadros


def por_do_sol_quadros():
    quadros = []
    n = 14
    for k in range(n):
        t = min(1.0, k / 9)
        img = Image.new("RGBA", (W, H))
        d = ceu(img, [(250, 150, 90), (250, 190, 120), (240, 120, 120)])
        sol_y = 10 + int(16 * t)
        d.ellipse((76, sol_y, 92, sol_y + 16), fill=(255, 230, 140, 255))
        d.rectangle((0, 30, W, 48), fill=(200, 110, 110, 255))  # a lagoa no fim de tarde
        for j in range(10):  # reflexo do sol tremendo na agua
            y = 32 + j * 2
            larg = 8 - j // 2 + (1 if (k + j) % 2 else 0)
            d.line((84 - larg, y, 84 + larg, y), fill=(255, 210, 140, 255))
        for x in range(0, W, 14):  # silhueta da outra margem
            d.ellipse((x - 5, 24, x + 11, 34), fill=(90, 50, 60, 255))
        d.rectangle((0, 48, W, H), fill=(110, 70, 60, 255))  # a margem ja escura
        # os dois sentados, de costas, no banco (cortados na cintura pelo encosto)
        incl = 0 if k < 6 else min(3, k - 5)  # a Isa encosta a cabeca no ombro dele
        for nome, x, dx in (("kayo", 50, 0), ("isa_casual", 66, -incl)):
            spr = sprite(nome, CIMA, 0).crop((0, 0, 64, 40))
            img.alpha_composite(spr, (x - 32 + dx, 64 - 40 + 2))
        d.rectangle((30, 56, 88, 59), fill=(56, 92, 52, 255))  # encosto do banco de praca
        d.rectangle((30, 61, 88, 64), fill=(56, 92, 52, 255))
        d.rectangle((32, 56, 33, H), fill=(40, 40, 46, 255))
        d.rectangle((85, 56, 86, H), fill=(40, 40, 46, 255))
        if k >= 9:
            coracao(d, 57, 28 - (k - 9), cor=1)
        quadros.append(img)
    return quadros


def aviao_quadros():
    quadros = []
    n = 22
    for k in range(n):
        img = Image.new("RGBA", (W, H))
        d = ceu(img, [(150, 200, 240), (210, 232, 250)])
        for cx, cy in ((20 + k, 10), (90 + k // 2, 16)):  # nuvens andando devagar
            d.ellipse((cx % (W + 20) - 20, cy, cx % (W + 20), cy + 6), fill=(250, 250, 255, 255))
        d.rectangle((0, 40, W, H), fill=(110, 150, 100, 255))
        d.rectangle((0, 44, W, 48), fill=(80, 80, 86, 255))  # a pista
        for x in range(0, W, 12):
            d.line((x, 46, x + 5, 46), fill=(246, 246, 240, 255))
        if k < 16:  # corre na pista, decola e vai embora
            x = 120 - k * 7
            sobe = 0 if k < 6 else (k - 6) ** 2 // 2
            s = 1.0 if k < 9 else max(0.3, 1.0 - (k - 9) * 0.1)
            aviao(d, x, 45 - sobe, s)
        # moldura do janelao e o Kayo de costas olhando
        d.rectangle((0, 0, W, 3), fill=(120, 124, 132, 255))
        for x in (0, 42, 84, W - 3):
            d.rectangle((x, 0, x + 2, H), fill=(120, 124, 132, 255))
        d.rectangle((0, 58, W, H), fill=(214, 216, 222, 255))  # parapeito
        colar(img, sprite("kayo", CIMA, 0), 22, chao=H + 6)
        quadros.append(img)
    return quadros


# ---------------- fase 3: o castelo no Japao ----------------

SAKURA = [(232, 144, 182, 255), (248, 186, 210, 255), (255, 222, 236, 255)]
CRISTAL = [(60, 70, 150, 255), (100, 140, 214, 255), (160, 206, 248, 255), (226, 244, 255, 255)]


def petalas(img, k, n=14, semente=0):
    """Petalas de cerejeira caindo, a mesma conta em todo quadro: a cena inteira e um ceu so."""
    d = ImageDraw.Draw(img)
    for j in range(n):
        x0 = (j * 47 + semente * 13) % W
        y = ((j * 23 + k * (2 + j % 3)) % (H + 8)) - 4
        x = x0 + int(4 * math.sin((k + j * 5) * 0.5))
        larg = 1 + (k + j) % 2
        d.rectangle((x, y, x + larg, y), fill=SAKURA[j % 3])


def fundo_castelo():
    """O ceu roxo da noite, a lua, o castelo recortado ao fundo e galhos de cerejeira na frente."""
    img = Image.new("RGBA", (W, H))
    d = ceu(img, [(16, 12, 34), (40, 30, 70), (90, 50, 90)])
    for j in range(12):
        d.point(((j * 37) % W, (j * 11) % 30), fill=(220, 220, 240, 255))
    d.ellipse((96, 6, 112, 22), fill=(250, 242, 214, 255))
    d.ellipse((99, 9, 104, 14), fill=(226, 216, 186, 255))
    # o castelo, em silhueta escura
    sil = (30, 26, 48, 255)
    d.rectangle((40, 30, 88, 56), fill=sil)
    for y, meia in ((26, 30), (14, 20), (4, 12)):
        d.polygon(((64 - meia - 4, y + 6), (64 + meia + 4, y + 6), (64 + meia - 4, y), (64 - meia + 4, y)), fill=sil)
        d.rectangle((64 - meia + 6, y + 6, 64 + meia - 6, y + 12), fill=sil)
    d.rectangle((62, 9, 65, 12), fill=CRISTAL[2])  # a janela de cristal la no alto
    for x in (50, 58, 70, 78):
        d.point((x, 40), fill=(250, 220, 140, 255))
    d.rectangle((0, 56, W, H), fill=(60, 56, 70, 255))  # o patio de pedra
    for x in range(0, W, 12):
        d.line((x, 56, x - 6, H), fill=(44, 40, 54, 255))
    # galhos de cerejeira entrando pelos cantos
    for (x0, y0, x1, y1) in ((0, 4, 22, 14), (W, 2, W - 26, 12)):
        d.line((x0, y0, x1, y1), fill=(60, 34, 30, 255), width=2)
        for j in range(9):
            cx = x0 + (x1 - x0) * j // 8
            cy = y0 + (y1 - y0) * j // 8 + (j % 3) - 1
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 2), fill=SAKURA[j % 2])
    return img


def fundo_salao():
    """O salao do trono por dentro: tatame, pilares vermelhos e o brilho frio dos cristais."""
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(26, 22, 40, 255))
    for x in range(0, W, 16):  # shoji no fundo, apagados
        d.rectangle((x + 1, 8, x + 14, 40), fill=(70, 64, 80, 255))
        d.line((x + 7, 8, x + 7, 40), fill=(40, 34, 50, 255))
        d.line((x + 1, 24, x + 14, 24), fill=(40, 34, 50, 255))
    for x in (12, 112):
        d.rectangle((x, 0, x + 6, 54), fill=(150, 30, 34, 255))
        d.rectangle((x, 0, x + 1, 54), fill=(200, 60, 52, 255))
    d.rectangle((0, 46, W, H), fill=(130, 126, 70, 255))  # tatame
    for x in range(0, W, 3):
        d.line((x, 46, x, H), fill=(110, 108, 58, 255))
    d.line((0, 46, W, 46), fill=(40, 50, 34, 255))
    for x, h in ((28, 12), (34, 18), (96, 16), (102, 10)):  # cristais crescendo do chao
        d.polygon(((x, 50 - h), (x - 3, 50 - h // 3), (x, 50), (x + 3, 50 - h // 3)), fill=CRISTAL[1])
        d.line((x, 50 - h + 1, x, 50 - h // 2), fill=CRISTAL[3])
    return img


def tatu_desperta_quadros():
    """O Tatu Cristal acorda: o casco brilha, a aura fria pulsa no chao e estilhacos giram em
    volta dele."""
    quadros = []
    tatu = sprite("tatu_cristal", ESQ, 0)
    n = 12
    for k in range(n):
        img = fundo_salao()
        d = ImageDraw.Draw(img)
        respira = 1 if k % 4 in (1, 2) else 0
        img.alpha_composite(tatu, (64 - 32, 62 - 63 - respira))
        # aura fria pulsando no chao
        raio = 26 + (k % 6)
        d.ellipse((64 - raio, 58, 64 + raio, 64), outline=CRISTAL[1])
        # estilhacos orbitando
        for j in range(5):
            ang = (k * 0.5) + j * (2 * math.pi / 5)
            x = 64 + int(34 * math.cos(ang))
            y = 36 + int(12 * math.sin(ang))
            d.polygon(((x, y - 3), (x + 2, y), (x, y + 3), (x - 2, y)), fill=CRISTAL[2 + (j + k) % 2])
        # um brilho correndo pelos cristais do casco
        gx = 50 + (k * 5) % 30
        d.line((gx, 30 - respira, gx + 3, 26 - respira), fill=(255, 255, 255, 255))
        quadros.append(img)
    return quadros


def cristal_quebra_quadros():
    """O cristal que prendia a Isa racha, brilha e explode em estilhacos; ela fica de pe, livre."""
    quadros = []
    presa = sprite("jp_isa_cristal", BAIXO, 0)
    livre = sprite("isa_japonesa", BAIXO, 0)
    rachas = [((64, 20), (58, 30), (62, 38)), ((64, 26), (72, 34), (68, 44)), ((58, 30), (52, 42)),
              ((62, 38), (60, 52)), ((72, 34), (76, 48)), ((68, 44), (66, 58))]
    for k in range(16):
        img = fundo_salao()
        d = ImageDraw.Draw(img)
        if k < 7:  # o cristal tremendo e rachando
            treme = (k % 2) * (1 if k > 2 else 0)
            img.alpha_composite(presa, (32 + treme, 64 - 63))
            for r in rachas[:k]:
                d.line([(x + treme, y) for x, y in r], fill=(255, 255, 255, 255))
        elif k == 7:  # o clarao
            d.rectangle((0, 0, W, H), fill=(230, 246, 255, 255))
        else:  # os estilhacos voando e a Isa livre
            img.alpha_composite(livre, (32, 64 - 63))
            t = k - 7
            for j in range(12):
                ang = j * (2 * math.pi / 12) + 0.3
                x = 64 + int(math.cos(ang) * t * 6)
                y = 36 + int(math.sin(ang) * t * 4) + t * t // 4
                if 0 <= x < W and 0 <= y < H:
                    d.polygon(((x, y - 2), (x + 2, y), (x, y + 2), (x - 2, y)), fill=CRISTAL[1 + j % 3])
            if t >= 4:
                for j, (bx, by) in enumerate(((48, 20), (80, 16), (56, 8))):
                    if (t + j) % 3:
                        d.point((bx, by), fill=(255, 255, 255, 255))
                        d.point((bx + 1, by + 1), fill=CRISTAL[3])
        quadros.append(img)
    return quadros


def beijo_quadros():
    """O abraco do reencontro no patio do castelo, e depois o beijo: as cabecas se encostam, um
    coracao grande e petalas caindo o tempo todo."""
    fundo = fundo_castelo()

    def chuva(img, k):
        petalas(img, k, n=16, semente=3)

    quadros = abraco_quadros(fundo, coracoes=True, n_squeeze=4, isa_spr="isa_japonesa", extra=chuva)
    lw, lh = W // 2, H // 2
    chao, centro = 60, lw // 2
    kayo, isa = sprite("kayo", DIR, 0), sprite("isa_japonesa", ESQ, 0)
    for k in range(10):
        img = Image.new("RGBA", (lw, lh))
        junto = 2 if k >= 2 else 3 - k  # chegam mais perto: o beijo
        pe = 1 if k >= 2 else 0  # ela fica na ponta dos pes
        colar(img, kayo, centro - junto, chao)
        colar(img, isa, centro + junto, chao, dy=-pe)
        d = ImageDraw.Draw(img)
        topo_y = chao - 63 + min(topo(kayo), topo(isa))
        if k >= 2:
            coracao(d, centro - 3, topo_y - 9 - (k % 2), cor=0, grande=True)
            for j, bx in enumerate((centro - 16, centro + 12, centro - 10, centro + 6)):
                sobe = ((k * 2 + j * 3) % 12)
                coracao(d, bx, topo_y + 14 - sobe, cor=1 + j % 2 if j % 2 else 1)
        out = fundo.copy()
        out.alpha_composite(img.resize((W, H), Image.NEAREST))
        petalas(out, len(quadros), n=16, semente=3)
        quadros.append(out)
    return quadros


def volta_casa_quadros():
    """Depois do beijo, a pergunta: os dois de frente, um mapa aberto entre eles e pontos de
    interrogacao pulando. A gota de suor e do Kayo."""
    quadros = []
    kayo, isa = sprite("kayo", BAIXO, 0), sprite("isa_japonesa", BAIXO, 0)
    for k in range(8):
        img = fundo_castelo()
        petalas(img, k, n=10, semente=7)
        colar(img, kayo, 46, chao=H - 2)
        colar(img, isa, 82, chao=H - 2)
        d = ImageDraw.Draw(img)
        # o mapa aberto, com o Brasil e o Japao nas pontas e um oceano enorme no meio
        d.rectangle((54, 40, 74, 52), fill=(236, 222, 180, 255))
        d.rectangle((54, 40, 74, 52), outline=(140, 110, 70, 255))
        d.rectangle((56, 44, 59, 49), fill=(90, 160, 70, 255))
        d.rectangle((71, 42, 72, 45), fill=(90, 160, 70, 255))
        d.line((60, 46, 70, 44), fill=(200, 40, 40, 255))
        d.point((65, 47), fill=(40, 40, 40, 255))
        for j, (x, y) in enumerate(((40, 6), (86, 4), (60, 2))):
            pulo = 2 if (k + j * 2) % 4 < 2 else 0
            d.text((x, y - pulo), "?", fill=(255, 240, 120, 255))
        if k % 4 < 3:  # a gota de suor do Kayo
            d.polygon(((56, 14 + k % 4), (58, 18 + k % 4), (54, 18 + k % 4)), fill=(120, 190, 255, 255))
        quadros.append(img)
    return quadros


def gravar(nome, quadros, segurar, volta):
    OUT.mkdir(parents=True, exist_ok=True)
    tira = Image.new("RGBA", (W * len(quadros), H))
    for i, q in enumerate(quadros):
        tira.alpha_composite(q, (i * W, 0))
    tira.save(OUT / f"{nome}.png", optimize=False)
    meta = {"frames": len(quadros), "hold": segurar, "loop_from": volta}
    (OUT / f"{nome}.json").write_bytes((json.dumps(meta, indent="\t") + "\n").encode("utf-8"))
    print(OUT / f"{nome}.png", len(quadros), "quadros")


def main():
    q = abraco_quadros(fundo_rodoviaria(), corre=True)
    gravar("abraco_chegada", q, [5] * 6 + [10] + [7] * 8, 7)
    fundo = Image.new("RGBA", (W, H), (250, 214, 226, 255))
    ImageDraw.Draw(fundo).rectangle((0, 58, W, H), fill=(236, 180, 200, 255))
    q = abraco_quadros(fundo)
    gravar("abraco", q, [6] * 6 + [10] + [7] * 8, 7)
    q = terere_quadros()
    gravar("terere", q, [14, 10, 10, 20, 10, 10, 12, 14, 10, 10, 20, 10, 10, 12], 0)
    q = por_do_sol_quadros()
    gravar("por_do_sol", q, [16] * 14, 10)
    q = abraco_quadros(fundo_aeroporto(), lagrimas=True, coracoes=False, n_squeeze=8)
    gravar("abraco_despedida", q, [12] * 6 + [24] + [14] * 8, 7)
    q = aviao_quadros()
    gravar("aviao", q, [10] * 6 + [8] * 10 + [14] * 6, 16)
    # fase 3
    q = tatu_desperta_quadros()
    gravar("tatu_desperta", q, [10] * 12, 2)
    q = cristal_quebra_quadros()
    gravar("cristal_quebra", q, [14, 10, 10, 10, 8, 8, 6, 8] + [8] * 7 + [20], 15)
    q = beijo_quadros()
    gravar("beijo", q, [6] * 6 + [10] + [8] * 4 + [12, 12] + [10] * 8, 13)
    q = volta_casa_quadros()
    gravar("volta_casa", q, [10] * 8, 0)


if __name__ == "__main__":
    main()
