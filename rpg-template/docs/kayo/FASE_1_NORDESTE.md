# Fase 1: Nordeste (Açailândia, Maranhão)

Primeira fase de **A Jornada do Kayo**. O Kayo recebe uma mensagem da Isa chamando ele para Três Lagoas e
descobre onde está no melhor estilo GeoGuessr. Na estrada de terra ele **captura** um Tatu e um Animal
Louco com as Cuiabolas do avô e, com os dois na equipe, vence os bichos do Marcos para pegar o ônibus
para Três Lagoas. A inspiração é Pokémon Fire Red: mundo vivo, bichos capturáveis e luta de treinador.

Sequência do jogo: **Nordeste → Três Lagoas (MS) → Japão**.

---

## Roteiro

| # | Cena | O que acontece |
|---|------|----------------|
| 1 | Casa de madeira | Abertura automática. Casa mobiliada: cama de chita, estante, filtro de barro, fogão a lenha, mesa com banquinhos e tapete. O celular aceso na mesa traz a mensagem da Isa (ela está em Três Lagoas). A porta só abre depois da mensagem lida. A estante dá 3 rapaduras e a mesa dá **5 Cuiabolas**. |
| 2 | Sertão (vila) | Mandacaru, xique-xique, palma, juazeiro, poço com balde, varal, potes de barro, tambor d'água, roda de carroça, bandeirinhas, capim seco, calangos, caveira de boi. **Bode e galinhas andando.** **Mecânica GeoGuessr:** examinar o poste, a placa e o mandacaru. Só com as 3 pistas a estrada a leste libera. |
| 3 | Estrada de terra | O Kayo fecha a rodada ("sertão do Maranhão, 5000 pontos"). Há postes na beira da estrada e um bode solto. Duas passagens com bichos selvagens: **"Um Tatu selvagem apareceu!"** e depois o Animal Louco. Dá para derrotá-los ou **capturá-los**. |
| 4 | Terreiro do Marcos | Um arraiá, com fogueira, bandeirinhas, banco e galinhas. O Marcos desafia no estilo treinador de Pokémon. A luta abre com o cartaz **"MARCOS QUER BATALHAR!"**, ele fica atrás dos bichos e grita a cada turno deles. Depois da vitória ele libera a passagem, e a placa do ônibus encerra a fase. |

A Isa **não aparece** no Nordeste. Ela fala só pelo celular, sem retrato, e os dois se encontram em Três Lagoas.
O **castelo e o chefão são só do Japão**. A mensagem está guardada em `data/dialog/japao_isa_castelo.json`.

## Combate

**Menu:** Ataque · Golpes · Item · **Pegar o beco** (fugir, em nordestinês). Tudo em português,
pelo arquivo `data/i18n/pt_BR.json`.

**Dano** = ataque − defesa (mínimo 1). Um golpe na hora certa causa o **dobro** de dano (o "reflexo do CS"), e
uma defesa na hora certa corta o dano pela metade. **Fôlego** (MP): 6 no nível 1, +2 por nível.

### Golpes e magias do Kayo

| Golpe | Nível | Fôlego | O que faz |
|-------|-------|--------|-----------|
| Lapada da Mísera | 1 | 3 | 8 de dano num inimigo, ignorando a defesa |
| Rajada Seca | 1 | 3 | vento seco: 5 de dano em **todos** os inimigos |
| Água Sagrada | 1 | 3 | cura **50% da vida máxima** ("pra nordestino, toda água é sagrada") |
| Cruz de Malta | 2 | 2 | bate no peito na cruz do Vasco: +3 de ataque por 3 turnos |
| Chicotada do Lampião | 2 | 4 | 11 de dano num inimigo, o golpe mais forte |
| Oxente! | 2 | 3 | o grito deixa um inimigo **abestado** (dormindo) por 2 turnos |

Cada golpe mostra um ícone sobre o Kayo (mão, vento, gota, cruz de malta, chicote, "?!").

### Captura (Cuiabola)

- **Cuiabola** é a "pokébola do sertão", feita de cuia. O Kayo acha 5 na mesa de casa.
- Use em **Item → Cuiabola** contra um bicho selvagem. A chance é de 35% com a vida cheia e cresce com o dano. Com **um terço da vida ou menos, a captura é garantida**: enfraqueça antes.
- **Animação:** a bola voa em arco, o bicho some num clarão, a bola balança três vezes no chão e então solta estrelas (capturou) ou estoura (escapou).
- Os bichos do Marcos **têm dono**: a bola é rebatida ("Esse bicho tem dono!") e se perde.
- Capturar conta como vencer a luta: dá XP, e o bicho sai do mapa.

### Parceiros capturados (lutam do lado do Kayo)

| Parceiro | Vida | Atq | Def | Fôlego | Golpe |
|----------|------|-----|-----|--------|-------|
| Tatu | 18 (+4/nível) | 4 | 3 | 4 | Rolada Blindada: 6 de dano |
| Animal Louco | 14 (+3/nível) | 6 | 1 | 6 | Doideira Coletiva: 4 de dano em todos |

Cada membro da equipe escolhe a própria ação, em ordem. Todos ganham XP inteiro.

### Inimigos

| Inimigo | Vida | Atq | Def | XP | Golpes |
|---------|------|-----|-----|----|--------|
| Tatu (selvagem, capturável) | 12 | 3 | 2 | 12 | Rolada, Cavucada |
| Animal Louco (selvagem, capturável) | 10 | 4 | 0 | 10 | Mordida, Surto |
| Tatu Treinado (Marcos) | 20 | 4 | 2 | 25 | Rolada Treinada, Casco |
| Animal Louco Treinado (Marcos) | 14 | 5 | 1 | 15 | Mordida, Surto Treinado |

Os dois selvagens somam 22 XP, então o Kayo chega ao Marcos no nível 2 e sai no nível 3. A luta do Marcos tem
música própria. Dá para fugir dela, mas os bichos continuam na passagem.

### Animações de batalha

- **Encontro:** a tela pisca, vem o cartaz ("Um Tatu selvagem apareceu!") e os bichos entram correndo pela direita.
- **Golpe:** quem apanha treme e pisca, o número de dano sobe e há faíscas de impacto. Um golpe na hora certa faz o campo inteiro tremer.
- **Magias:** a Rajada Seca e a Doideira varrem todos com um risco, a cura faz gotas caírem, o bônus solta faíscas com "ATQ+" e o "Oxente!" solta faíscas no alvo.
- **Derrota:** o bicho caído desbota em vez de sumir.
- **Marcos:** cartaz próprio, ele dá um passo à frente na abertura e grita no balão ("Vai, Tatu! Rola nele!", "Morde, Animal Louco!", ...).

## Mapas

**kayo_casa** (11×8): o Kayo começa em (5,5). Celular em (8,4), Cuiabolas em (7,4), pote de rapadura na estante em (4,1) e porta em (5,7).

**kayo_vila** (20×13): porta da casa em (3,3). Pistas: poste (12,6), placa (10,8) e mandacaru (16,4).
Bode passeando em volta de (4,10). Galinhas em (7,2) e (14,10). Saída leste em (19,7).

**kayo_estrada** (22×9): Tatu em (7,4), Animal Louco em (14,4), bode em (10,6) e saída em (21,4).

**kayo_terreiro** (14×10): Marcos em (7,3), os bichos dele em (8,5), fogueira em (4,3), galinhas e ponto de ônibus em (11,5).

## Flags da fase

| Flag | Quando é marcada |
|------|-----------|
| `acordou` | abertura vista |
| `leu_mensagem` | mensagem da Isa lida (abre a porta) |
| `pista_poste`, `pista_placa`, `pista_mandacaru` | cada pista examinada |
| `pistas_nordeste` | as 3 pistas (abre a estrada) |
| `leu_a_estrada` | conclusão do GeoGuessr vista |
| `pegou_tatu`, `pegou_louco` | bicho capturado (entra na equipe) |
| `marcos_desafiou` | desafio do Marcos visto |
| `fase1_completa` | placa do ponto de ônibus lida |

## Arquivos

| O quê | Onde (`rpg-template/`) |
|-------|------------------------|
| Mapas | `data/maps/kayo_casa.json`, `kayo_vila.json`, `kayo_estrada.json`, `kayo_terreiro.json` |
| Diálogos | `data/dialog/` (`intro_casa`, `mensagem_isa`, `cuiabolas`, `pista_*`, `marcos_*`, `bode`, `galinha`, `fim_fase1`...) |
| Golpes | `data/spells/` (`lapada_da_misera`, `rajada_seca`, `agua_sagrada`, `cruz_de_malta`, `chicotada_do_lampiao`, `oxente`, `rolada_blindada`, `doideira_coletiva`) |
| Inimigos | `data/enemies/tatu.tres`, `animal_louco.tres`, `tatu_marcos.tres`, `animal_louco_marcos.tres` |
| Parceiros | `data/party/parceiro_tatu.tres`, `parceiro_louco.tres` (+ `data/combat/parceiro_*_combat.tres`) |
| Combate do Kayo | `data/combat/kayo_combat.tres` |
| Itens | `data/items/rapadura.tres`, `cuiabola.tres` |
| Tradução | `data/i18n/pt_BR.json` |
| Código do jogo | `games/kayo/kayo_hooks.gd` |
| Manifesto | `data/games/kayo.tres` |
| Ícones | `assets/kayo/icons/` |
| Tiles | `data/imports/tiles/lpc32/sertao.png` → bancos `data/tiles/lpc32.json` e `gb16.json` |
| Testes de jogo | `tests/fixtures/qa/kayo/boots.json`, `fase1_completa.json` |

Geradores (na raiz `game_kayo/`):
- `tools/gerar_tiles_sertao.py`: os 37 tiles do sertão (chão, decoração, móveis e vida), mais a versão 16px.
- `tools/gerar_sprites.py`: personagens de foto, as tiras do tatu e do animal louco, o bode e a galinha.
- `tools/gerar_bichos.py`: desenha as tiras de caminhada do bode e da galinha.
- `tools/gerar_icones.py`: os ícones dos golpes e da Cuiabola.

Depois de mudar arte, rode os geradores e então, dentro de `rpg-template/`:
```
godot --headless --path . -s tools/gen_sprites.gd
godot --headless --path . --import
```

## Mudanças no código do template

O pedido de golpes, menu em português, animações e captura exigiu mudar o código do template. Todas as
mudanças são **opcionais por dado**: um jogo que não usa os campos novos funciona como antes, e o demo
continua igual.

| Mudança | Onde |
|---------|------|
| `CombatDef.spells`: lista de golpes do líder de cada jogo. Antes os dois jogos trocavam magias entre si. | `combat_def.gd`, `battle_logic.gd` (`leader_page`), `world_scene.gd` |
| `CombatDef.wild_intro`: cartaz de encontro selvagem | `combat_def.gd`, `battle_screen.gd` |
| `SpellDef.percent`: cura em porcentagem. `SpellDef.icon`: ícone do golpe. | `spell_def.gd`, `battle_logic.gd` |
| `ItemDef.capture` + `icon`, `EnemyDef.caught_flag`: captura | `item_def.gd`, `enemy_def.gd`, `battle_logic.gd` (`_throw`) |
| `EnemyDef.presenter` / `intro` / `presenter_lines`: treinador atrás da formação | `enemy_def.gd`, `battle_screen.gd` |
| `GameManifest.language` + `data/i18n/<id>.json`: tradução | `game_manifest.gd`, `scripts/util/i18n.gd`, `world_scene.gd`, `prompts.gd`, `ui_chrome.gd`, frases do combate em `tr()` |
| Camada de animações da batalha | `scripts/ui/battle_fx.gd` (novo), `battle_screen.gd` |

Testes do template ajustados para refletir dois jogos no mesmo projeto: `test_world_battles` (lista de campos e
magias do demo), `battle_helpers` (usa `leader_page`) e `test_battle_content` (item de captura no menu; cobertura
de golpes por jogo). Duas âncoras de mutação foram atualizadas para as frases com `tr()`.

## Validação (29/10/2026)

- **Sessão de jogo automática `fase1_completa.json`: OK (308 passos).** Ela joga a fase inteira: porta trancada
  antes do celular, rapaduras e Cuiabolas uma vez só, estrada trancada antes das pistas, as 3 pistas,
  **captura do Tatu e do Animal Louco** (Lapada da Mísera e depois Cuiabola), a luta contra os bichos do Marcos
  **com a equipe de três** (nível 3), a fala depois da luta e o ponto de ônibus.
- `boots.json`: OK. `lint_rules`: sem violações. `compile_all`: OK. `smoke_boot`: OK.
- Suíte do template: 1788 casos, 5 falhas em 2 testes, nenhum ligado à fase. São as mesmas de antes:
  - `test_title`: espera um projeto com um jogo só, e hoje há dois. Some quando o demo sair.
  - `test_ci_paths`: o `fetch_godot.sh` não acha o `sha512sum` pelo bash que o Godot chama no Windows (ambiente).
- Capturas de tela conferidas: casa, vila, estrada, cartaz selvagem, menu, captura (voo, balanço e fuga), luta do
  Marcos com a equipe, Cruz de Malta, balão do Marcos.

## Decisões e limitações

- **O Marcos usa o personagem `town_smith` do LPC.** Não havia arte dele.
- **O Marcos é o chefe-treinador**, e a luta dele permite fuga (o template aceita um só chefe sem fuga, e esse é o do demo).
- **"Cuiabola" em vez de "Pokébola"**: o nome é uma marca registrada, e a cuia dá o sotaque nordestino.
- **Ids internos com prefixo** (`tatu_cristal`, `louco`, `sertao_bode`, `sertao_galinha`): um teste do template fixa o primeiro personagem do elenco em ordem alfabética. Os nomes na tela não mudam.
- **"Chicotada do Lampião"** é longo: no menu o custo dela fica cortado.
- **Água Sagrada e Oxente!** ainda não são usados pela sessão automática. Os outros golpes são.
- **Animações e cartazes só no modo por turnos** (o padrão). O modo arena, escolhido em Opções, não tem.
- **As músicas são as do demo.**
- Telas fora do combate (pausa, status, loja) ainda têm textos em inglês que não estão no arquivo de tradução.

## Próximo

**Fase 2: Três Lagoas (MS)**, já pronta: [FASE_2_TRES_LAGOAS.md](FASE_2_TRES_LAGOAS.md). A placa do
ponto de ônibus abre a estrada a leste do terreiro (13,4), que leva à rodoviária de Três Lagoas.
O plano das fases está em [PLANO.md](PLANO.md).
