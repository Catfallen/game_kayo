"""Gera sprite sheets de caminhada (4 direcoes) a partir de uma unica imagem por personagem.

Saida no contrato do rpg-template: <id>.png + <id>.sheet.json, celulas quadradas,
linhas na ordem down, left, right, up; coluna 0 = parado, colunas 1-8 = caminhada.

As vistas que nao existem na foto original sao SINTETIZADAS:
  - lado:  a frente comprimida na horizontal (ou a propria arte, se ja estiver de lado)
  - costas: a frente espelhada com o rosto coberto pela cor do cabelo
  - passos: pernas deslocadas/inclinadas quadro a quadro + leve balanco do corpo
Sao aproximacoes para prototipo; um artista pode retocar os PNGs gerados.

Uso:  python -I tools/gerar_sprites.py [pasta_assets] [pasta_saida]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

DIRS = ["down", "left", "right", "up"]
WALK_FRAMES = 8

# height: altura do personagem em px dentro da celula.
# leg_top: fracao da altura onde comecam as pernas (o que se move ao andar).
# head_bottom: fracao da altura onde termina a cabeca (usado no retrato e nas costas).
# view: "front" (foto de frente), "front_right" (frente olhando p/ direita), "side_left" (perfil p/ esquerda).
CHARS = {
    "kayo": dict(src="personagem kayo.png", cell=64, height=56, view="front",
                 leg_top=0.62, head_bottom=0.32, stride=4, lift=3, colors=30, nape=True),
    "isa_casual": dict(src="isa casual.png", cell=64, height=48, view="front_right",
                       leg_top=0.56, head_bottom=0.24, stride=3, lift=2, colors=20),
    "isa_japonesa": dict(src="isa japonesa.png", cell=64, height=48, view="front_right",
                         leg_top=0.84, head_bottom=0.25, stride=1, lift=1, colors=20),
    # criatura: o corpo nao se separa das pernas, entao so os pes levantam (walk="lift").
    # Celula 64 porque o estilo lpc32 do template so importa quadros LPC de 64x64.
    "tatu_cristal": dict(src="Chefe.png", cell=64, height=58, view="side_left", walk="lift",
                  leg_top=0.88, head_bottom=0.40, stride=3, lift=2, colors=20),
}

# Tiras de animacao ja desenhadas (quadros lado a lado, perfil virado para a direita).
# Aqui nada e sintetizado: os 8 quadros da caminhada sao amostrados da propria tira.
STRIPS = {
    "tatu": dict(src="tatu.png", frames=16, cell=64, height=26, colors=20, portrait=22),
    "louco": dict(src="animal_louco.png", frames=13, cell=64, height=24, colors=20, portrait=20),
    # bichos que andam pelos mapas (desenhados por tools/gerar_bichos.py). Prefixo sertao_ porque o
    # teste do Sprite Lab do template exige que o primeiro do elenco em ordem alfabetica seja o dele.
    "sertao_bode": dict(src="bichos/bode.png", frames=8, cell=64, height=30, colors=16, portrait=22),
    "sertao_galinha": dict(src="bichos/galinha.png", frames=8, cell=64, height=23, colors=12, portrait=18),
    # a capivara da Lagoa Maior (fase 2, Tres Lagoas). Prefixo tl_ pelo mesmo motivo do sertao_.
    "tl_capivara": dict(src="bichos/capivara.png", frames=8, cell=64, height=24, colors=14, portrait=20),
    # a Isa presa no cristal do Tatu, no salao do castelo (fase 3). Prefixo jp_ pelo mesmo motivo.
    "jp_isa_cristal": dict(src="bichos/isa_cristal.png", frames=8, cell=64, height=60, colors=24, portrait=22),
}

# Credito gravado no character.json de cada personagem exportado para o template. O importador
# exige uma licenca da lista do estilo lpc32 (CC0, CC-BY, OGA-BY, CC-BY-SA); ajuste autor e
# licenca aqui e rode de novo - a tela de Creditos do jogo mostra exatamente isto.
CREDIT = {
    "authors": ["Projeto de faculdade game_kayo"],
    "licenses": ["CC-BY 4.0"],
    "urls": [],
    "notes": "Sprites de caminhada gerados por tools/gerar_sprites.py a partir de uma ilustracao unica.",
}

# Layout de entrada do importador LPC do template (scripts/spritegen/lpc_import.gd):
# quadros de 64px, 13 colunas, caminhada nas linhas 8-11 na ordem up, left, down, right.
LPC_FRAME = 64
LPC_COLUMNS = 13
LPC_WALK_ROW = 8
LPC_ROW_ORDER = ["up", "left", "down", "right"]


# ---------- preparo da arte base ----------

def load_base(path: Path, height: int, colors: int) -> np.ndarray:
    """Recorta o personagem, reduz para `height` px e devolve RGBA uint8 com alfa binario."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    ys, xs = np.nonzero(a[..., 3] >= 128)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w = max(1, round(im.width * height / im.height))
    return quantize(shade(shrink(im, w, height)), colors)


def shade(a: np.ndarray) -> np.ndarray:
    """Gradiente vertical (cabeca mais clara, pes mais escuros) MAIS um gradiente horizontal por
    linha (mais claro no centro de cada silhueta, mais escuro nas bordas) - sem os dois, a
    reducao+quantizacao vira uma silhueta uniforme (efeito 'papelao', sem volume nenhum)."""
    h, w = a.shape[:2]
    opaque = a[..., 3] > 0
    rows = np.nonzero(opaque.any(1))[0]
    if len(rows) < 2:
        return a
    y0, y1 = int(rows.min()), int(rows.max())
    vspan = max(1, y1 - y0)
    vfac = 1.22 - 0.46 * (np.arange(h) - y0) / vspan
    vfac = np.clip(vfac, 0.64, 1.22)
    out = a.copy()
    rgb = out[..., :3].astype(np.float64)
    xs_all = np.arange(w)
    for y in range(h):
        xs = np.flatnonzero(opaque[y])
        if len(xs) == 0:
            continue
        cx = (xs[0] + xs[-1]) / 2
        half = max(1, (xs[-1] - xs[0]) / 2)
        hfac = 1.0 - 0.24 * np.abs(xs_all - cx) / half
        hfac = np.clip(hfac, 0.78, 1.0)
        rgb[y] *= (vfac[y] * hfac)[:, None]
    out[..., :3] = np.where(opaque[..., None], rgb.clip(0, 255), out[..., :3])
    return out


def shrink(im: Image.Image, w: int, h: int) -> np.ndarray:
    """Reducao por media com alfa pre-multiplicado (nao vaza cor do fundo transparente)."""
    arr = np.array(im).astype(np.float64)
    arr[..., :3] *= arr[..., 3:4] / 255.0
    small = np.array(Image.fromarray(arr.clip(0, 255).astype(np.uint8)).resize((w, h), Image.BOX)).astype(np.float64)
    alpha = np.array(im.getchannel("A").resize((w, h), Image.BOX)).astype(np.float64)
    rgb = np.where(alpha[..., None] > 0, small[..., :3] * 255.0 / np.maximum(alpha[..., None], 1), 0)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = rgb.clip(0, 255)
    out[..., 3] = np.where(alpha >= 110, 255, 0)
    return out


def quantize(a: np.ndarray, colors: int) -> np.ndarray:
    """Limita a paleta para manter o visual de pixel art apos a reducao."""
    mask = a[..., 3] > 0
    rgb = Image.fromarray(a[..., :3])
    q = np.array(rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB"))
    out = a.copy()
    out[..., :3] = np.where(mask[..., None], q, 0)
    return out


def outline(a: np.ndarray) -> np.ndarray:
    """Contorno escuro de 1px em volta da silhueta (o estilo LPC tem contorno)."""
    h, w = a.shape[:2]
    p = np.zeros((h + 2, w + 2, 4), np.uint8)
    p[1:-1, 1:-1] = a
    solid = p[..., 3] > 0
    grow = np.zeros_like(solid)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        grow |= np.roll(np.roll(solid, dy, 0), dx, 1)
    edge = grow & ~solid
    # cor do contorno: o vizinho opaco escurecido
    col = np.zeros((h + 2, w + 2, 3), np.float64)
    cnt = np.zeros((h + 2, w + 2, 1), np.float64)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s = np.roll(np.roll(p, dy, 0), dx, 1)
        m = (s[..., 3] > 0)[..., None]
        col += s[..., :3] * m
        cnt += m
    dark = (col / np.maximum(cnt, 1) * 0.30).astype(np.uint8)
    p[edge, :3] = dark[edge]
    p[edge, 3] = 255
    return p


def is_skin(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    return (r > 140) & (r > g) & (g > b) & (r - b > 35) & (r - b < 140)


# ---------- vistas ----------

def squash(a: np.ndarray, factor: float) -> np.ndarray:
    """Comprime na horizontal escolhendo colunas (vizinho mais proximo, sem borrar)."""
    h, w = a.shape[:2]
    nw = max(1, round(w * factor))
    cols = np.clip(((np.arange(nw) + 0.5) * w / nw).astype(int), 0, w - 1)
    return a[:, cols]


def back_view(a: np.ndarray, head_bottom: float, nape: bool = False) -> np.ndarray:
    """Costas: espelha e cobre o rosto com a cor de cabelo dominante da cabeca.

    nape=True deixa o terco de baixo do rosto com cor de pele (nuca), para cabelo curto.
    """
    b = a[:, ::-1].copy()
    hb = max(1, round(b.shape[0] * head_bottom))
    head = b[:hb]
    opaque = head[..., 3] > 0
    skin = is_skin(head[..., :3]) & opaque
    hair_px = head[opaque & ~skin][:, :3]
    if len(hair_px) == 0:
        return b
    lum = hair_px.astype(int).sum(1)
    dark = hair_px[lum <= np.percentile(lum, 40)]
    vals, counts = np.unique(dark, axis=0, return_counts=True)
    hair = vals[counts.argmax()]
    # o rosto e o retangulo que envolve toda a pele da cabeca (inclui olhos e boca)
    sy, sx = np.nonzero(skin)
    if len(sy) == 0:
        return b
    face = np.zeros_like(opaque)
    face[sy.min():sy.max() + 1, sx.min():sx.max() + 1] = True
    face &= opaque
    shine = np.clip(hair.astype(int) * 1.5 + 50, 0, 255).astype(np.uint8)
    skin_tone = np.median(head[skin][:, :3], axis=0).astype(np.uint8)
    head[face, :3] = hair
    x0, x1 = sx.min(), sx.max() + 1
    fw = x1 - x0
    if nape:
        # nuca: as 3 ultimas linhas do rosto, so no meio (o pescoco e mais estreito que a cabeca)
        neck = np.zeros_like(face)
        neck[sy.max() - 2:sy.max() + 1, x0 + fw // 4:x1 - fw // 4] = True
        head[neck & face, :3] = skin_tone
    # um reflexo curto no cabelo, a um terco do rosto, para nao virar uma mancha chapada
    ry = sy.min() + (sy.max() - sy.min()) // 3
    head[ry, x0 + fw // 3:x1 - fw // 3, :3] = np.where(face[ry, x0 + fw // 3:x1 - fw // 3, None], shine, head[ry, x0 + fw // 3:x1 - fw // 3, :3])
    return b


def turn_head(a: np.ndarray, head_bottom: float, dx: int) -> np.ndarray:
    """Desloca a cabeca dx px na horizontal: o rosto 'aponta' para onde o corpo anda."""
    # a cabeca e mais estreita que o corpo, entao as bordas dessas linhas sao transparentes e o roll nao vaza
    out = a.copy()
    hb = round(a.shape[0] * head_bottom)
    out[:hb] = np.roll(a[:hb], dx, axis=1)
    return out


def views(base: np.ndarray, cfg: dict) -> dict:
    v = cfg["view"]
    if v == "front":
        right = turn_head(squash(base, 0.70), cfg["head_bottom"], 1)
        return {"down": base, "right": right, "left": right[:, ::-1],
                "up": back_view(base, cfg["head_bottom"], cfg.get("nape", False))}
    if v == "front_right":
        right = squash(base, 0.80)
        return {"down": base, "right": right, "left": right[:, ::-1], "up": back_view(base, cfg["head_bottom"])}
    if v == "side_left":
        # criatura de perfil: nao ha frente/costas na arte; usa o perfil nas quatro linhas
        return {"left": base, "right": base[:, ::-1], "down": base, "up": base[:, ::-1]}
    raise ValueError(v)


# ---------- animacao ----------

def walk_frame(a: np.ndarray, i: int, side: bool, cfg: dict) -> tuple:
    """Devolve (imagem, deslocamento vertical do corpo) do quadro i da caminhada."""
    h, w = a.shape[:2]
    s = math.sin(2 * math.pi * i / WALK_FRAMES)
    lt = round(h * cfg["leg_top"])
    body = a.copy()
    body[lt:] = 0
    legs = a.copy()
    legs[:lt] = 0
    opaque_cols = np.flatnonzero(legs[..., 3].any(0))
    mid = (opaque_cols.min() + opaque_cols.max() + 1) // 2 if len(opaque_cols) else w // 2
    # folga em volta para os deslocamentos; o pixel (y, x) do sprite fica em (y + pad, x + pad)
    pad = 4
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)

    def paste(img, dx, dy):
        ys, xs = np.nonzero(img[..., 3] > 0)
        out[ys + dy + pad, xs + dx + pad] = img[ys, xs]

    a_half = legs.copy(); a_half[:, mid:] = 0   # metade esquerda da imagem
    b_half = legs.copy(); b_half[:, :mid] = 0   # metade direita
    if side:
        # tesoura: cada perna inclina para um lado, proporcional a distancia do quadril
        span = max(1, h - lt)
        for half, sign in ((a_half, -1), (b_half, 1)):
            sheared = np.zeros_like(half)
            for y in range(lt, h):
                off = round(sign * s * cfg["stride"] * (y - lt) / span)
                row = half[y]
                if off > 0:
                    sheared[y, off:] = row[:w - off]
                elif off < 0:
                    sheared[y, :w + off] = row[-off:]
                else:
                    sheared[y] = row
            lift = -cfg["lift"] // 2 if sign * s > 0.5 else 0
            paste(sheared, 0, lift)
    else:
        paste(a_half, 0, -round(max(0.0, s) * cfg["lift"]))
        paste(b_half, 0, -round(max(0.0, -s) * cfg["lift"]))
    bob = 1 if abs(s) > 0.7 else 0
    paste(body, 0, bob)
    return out, pad


def build(cid: str, cfg: dict, src_dir: Path, out_dir: Path) -> None:
    base = outline(load_base(src_dir / cfg["src"], cfg["height"], cfg["colors"]))
    cell = cfg["cell"]
    foot_y = cell - 2  # mesma linha de chao dos personagens LPC do template (ancora y=62)
    vs = views(base, cfg)
    sheet = np.zeros((cell * 4, cell * (1 + WALK_FRAMES), 4), np.uint8)
    for row, d in enumerate(DIRS):
        img = vs[d]
        side = d in ("left", "right") and cfg.get("walk") != "lift"
        for col in range(1 + WALK_FRAMES):
            if col == 0:
                fr, pad = walk_frame(img, 0, side, dict(cfg, stride=0, lift=0))
            else:
                fr, pad = walk_frame(img, col - 1, side, cfg)
            # base dos pes do sprite parado em foot_y, centro horizontal no meio da celula
            h, w = img.shape[:2]
            ys, xs = np.nonzero(fr[..., 3] > 0)
            ty = ys - (h - 1 + pad) + foot_y
            tx = xs - (w // 2 + pad) + cell // 2
            ok = (ty >= 0) & (ty < cell) & (tx >= 0) & (tx < cell)
            tgt = sheet[row * cell:(row + 1) * cell, col * cell:(col + 1) * cell]
            tgt[ty[ok], tx[ok]] = fr[ys[ok], xs[ok]]
    # retrato: quadrado em volta da cabeca no quadro parado de frente
    f0 = sheet[:cell, :cell]
    ys, xs = np.nonzero(f0[..., 3] > 0)
    top = int(ys.min())
    head_h = max(8, round(cfg["height"] * cfg["head_bottom"]))
    size = min(cell, head_h + 4 + (head_h % 2))
    px = cell // 2 - size // 2
    py = max(0, min(cell - size, top - 2))
    write_sheet(cid, sheet, cell, foot_y, [px, py, size, size], "photo", out_dir)


def build_strip(cid: str, cfg: dict, src_dir: Path, out_dir: Path) -> None:
    """Folha a partir de uma tira de quadros de perfil (virada para a direita)."""
    im = Image.open(src_dir / cfg["src"]).convert("RGBA")
    a = np.array(im)
    ys = np.nonzero((a[..., 3] >= 128).any(1))[0]
    # recorte vertical comum a todos os quadros, para que a escala e a linha do chao sejam iguais
    im = im.crop((0, ys.min(), im.width, ys.max() + 1))
    f = cfg["height"] / im.height
    small = quantize(shrink(im, round(im.width * f), cfg["height"]), cfg["colors"])
    fw = im.width / cfg["frames"]
    chunks = [outline(small[:, round(k * fw * f):round((k + 1) * fw * f)]) for k in range(cfg["frames"])]
    picks = [round(i * cfg["frames"] / WALK_FRAMES) for i in range(WALK_FRAMES)]
    cell = cfg["cell"]
    foot_y = cell - 2
    sheet = np.zeros((cell * 4, cell * (1 + WALK_FRAMES), 4), np.uint8)
    for row, d in enumerate(DIRS):
        flip = d in ("left", "up")  # sem frente/costas na arte: baixo usa o perfil direito, cima o esquerdo
        for col in range(1 + WALK_FRAMES):
            fr = chunks[picks[col - 1] if col else 0]
            if flip:
                fr = fr[:, ::-1]
            h, w = fr.shape[:2]
            yy, xx = np.nonzero(fr[..., 3] > 0)
            ty = yy - (h - 1) + foot_y
            tx = xx - w // 2 + cell // 2
            ok = (ty >= 0) & (ty < cell) & (tx >= 0) & (tx < cell)
            tgt = sheet[row * cell:(row + 1) * cell, col * cell:(col + 1) * cell]
            tgt[ty[ok], tx[ok]] = fr[yy[ok], xx[ok]]
    # retrato: a cabeca fica na ponta direita do perfil; o quadrado precisa cruzar o centro (ancora.x)
    f0 = sheet[:cell, :cell]
    yy, xx = np.nonzero(f0[..., 3] > 0)
    size = cfg["portrait"]
    px = max(cell // 2 - size + 1, min(cell // 2, int(xx.max()) + 1 - size))
    py = max(0, min(cell - size, int(yy.min()) - 2))
    write_sheet(cid, sheet, cell, foot_y, [px, py, size, size], "strip", out_dir)


def write_sheet(cid: str, sheet: np.ndarray, cell: int, foot_y: int, portrait: list, source: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(sheet).save(out_dir / f"{cid}.png")
    meta = {
        "anchor": [cell // 2, foot_y + 1],
        "animations": {
            "idle": {"fps": 4, "frames": [0], "loop": True},
            "walk": {"fps": 8, "frames": list(range(1, 1 + WALK_FRAMES)), "loop": True},
        },
        "cell": [cell, cell],
        "character": cid,
        "columns": 1 + WALK_FRAMES,
        "directions": DIRS,
        "portrait": portrait,
        "rows": 4,
        "seed": 0,
        "source": source,
        "style": "lpc32",
        "version": 2,
    }
    (out_dir / f"{cid}.sheet.json").write_text(json.dumps(meta, indent="\t", sort_keys=True) + "\n", encoding="utf-8")
    print(f"{cid}: {sheet.shape[1]}x{sheet.shape[0]} (celula {cell})")


def preview(out_dir: Path, ids: list) -> None:
    """Folha ampliada x3 com todos os personagens + GIF animado por personagem."""
    for cid in ids:
        meta = json.loads((out_dir / f"{cid}.sheet.json").read_text(encoding="utf-8"))
        cell = meta["cell"][0]
        sheet = Image.open(out_dir / f"{cid}.png")
        frames = []
        for col in range(1, 1 + WALK_FRAMES):
            canvas = Image.new("RGBA", (cell * 4, cell), (90, 140, 80, 255))
            for row in range(4):
                fr = sheet.crop((col * cell, row * cell, (col + 1) * cell, (row + 1) * cell))
                canvas.alpha_composite(fr, (row * cell, 0))
            frames.append(canvas.resize((cell * 4 * 3, cell * 3), Image.NEAREST).convert("RGB"))
        frames[0].save(out_dir / "preview" / f"{cid}_andando.gif", save_all=True,
                       append_images=frames[1:], duration=125, loop=0)
        big = Image.new("RGBA", sheet.size, (90, 140, 80, 255))
        big.alpha_composite(sheet)
        big.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).convert("RGB").save(out_dir / "preview" / f"{cid}_folha_x3.png")


def export_lpc(out_dir: Path, imports_dir: Path, ids: list) -> None:
    """Reescreve cada folha no layout de entrada LPC: <imports>/<id>/sheet.png + character.json."""
    for cid in ids:
        meta = json.loads((out_dir / f"{cid}.sheet.json").read_text(encoding="utf-8"))
        cell = meta["cell"][0]
        if cell != LPC_FRAME:
            raise SystemExit(f"{cid}: celula {cell}; o importador LPC so aceita {LPC_FRAME}")
        sheet = Image.open(out_dir / f"{cid}.png")
        lpc = Image.new("RGBA", (LPC_FRAME * LPC_COLUMNS, LPC_FRAME * (LPC_WALK_ROW + 4)), (0, 0, 0, 0))
        for i, d in enumerate(LPC_ROW_ORDER):
            src_row = meta["directions"].index(d)
            strip = sheet.crop((0, src_row * cell, meta["columns"] * cell, (src_row + 1) * cell))
            lpc.paste(strip, (0, (LPC_WALK_ROW + i) * LPC_FRAME))
        dest = imports_dir / cid
        dest.mkdir(parents=True, exist_ok=True)
        lpc.save(dest / "sheet.png")
        recipe = {
            "bodyType": "photo",
            "credits": [dict(CREDIT, file=f"game_kayo/assets/{({**CHARS, **STRIPS})[cid]['src']}")],
            "generatedBy": "game_kayo/tools/gerar_sprites.py",
            "layers": [],
        }
        (dest / "character.json").write_text(json.dumps(recipe, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  importacao LPC: {dest}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "assets"
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "assets" / "sprites"
    imports_dir = root / "rpg-template" / "data" / "imports" / "lpc32"
    (out_dir / "preview").mkdir(parents=True, exist_ok=True)
    for cid, cfg in CHARS.items():
        build(cid, cfg, src_dir, out_dir)
    for cid, cfg in STRIPS.items():
        build_strip(cid, cfg, src_dir, out_dir)
    ids = list(CHARS) + list(STRIPS)
    preview(out_dir, ids)
    if imports_dir.parent.is_dir():
        export_lpc(out_dir, imports_dir, ids)


if __name__ == "__main__":
    main()
