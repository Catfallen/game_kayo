# Fase 3: Japão

Alguns dias depois da despedida em Três Lagoas, chega uma mensagem estranha: a Isa está presa num
castelo no Japão e tem um chefão que não a deixa sair. O Kayo atravessa o mundo, passa pela vila
das cerejeiras e pelo pátio do castelo e enfrenta o Tatu Cristal no salão do trono. O cristal que
prendia a Isa se quebra. Os dois têm a conversa final, que é melancólica, e se abraçam e se beijam.
Depois vem a pergunta que ninguém tinha feito: "como é que a gente vai voltar pra casa?". Então rolam
os créditos animados.

Pedido do dono e plano geral: [PLANO.md](PLANO.md).

## Roteiro

1. **Aeroporto de Três Lagoas** (`tl_aeroporto`, a ponte vinda da fase 2)
   - O janelão (`janela_aviao`) fecha a fase 2.
   - Na mesma conversa chega a mensagem da Isa presa no castelo. Antes ela ficava num arquivo à
     parte, `japao_isa_castelo`, que foi juntado aqui.
   - A porta da direita do saguão (17,6) é o **embarque internacional**. Ela fica trancada
     (`embarque_fechado`) até `fase2_completa`.
2. **Vila** (`jp_vila`)
   - É noite. As cerejeiras perdem as pétalas, que caem pela tela inteira, e o mapa tem um tom roxo.
   - A chegada abre `japao_chegada`.
   - A **Obaachan** dá 3 rapaduras uma vez só ("um moço do Maranhão esqueceu aqui").
   - O menino e a placa dão o tom da vila.
   - O torii é visto de frente, então só se passa por baixo dele indo para o norte, pelo vão do
     meio. Dali se chega ao caminho do castelo.
3. **Pátio do castelo** (`jp_patio`)
   - O castelo inteiro, com três telhados, peixes dourados e a janela de cristal brilhando, fecha o
     norte do mapa. A porta dele é o warp para o salão.
   - A chegada abre `patio_chegada`: a voz da Isa vem lá de dentro.
   - O **Monge** oferece descanso completo antes do chefe e explica a defesa: "olhe o brilho chegando
     e defenda no impacto".
   - Também há o lago das carpas, lanternas de pedra e um pinheiro de jardim.
4. **Salão do trono** (`jp_salao`)
   - A primeira entrada abre `tatu_desafio`, com a cena `tatu_desperta`: o Tatu Cristal acorda e
     chama a Isa de "a joia da minha coleção".
   - Uma parede de cristal atravessa o salão, e o único vão é onde o chefe está. A luta é
     inevitável pela geometria do mapa, a regra do template.
   - **A luta** é descrita logo abaixo.
   - Depois da vitória, falar com a Isa presa abre `cristal_quebra`. Na cena, o cristal treme,
     racha e explode em estilhaços, e isso marca `isa_livre`.
   - A Isa presa some e a Isa livre aparece no mesmo tile.
   - Falar com ela abre `final_isa`:
     - **Melancólica**: o avião virando um pontinho, o frio e o silêncio dentro do cristal, o medo
       de esquecer o calor das coisas.
     - **O abraço e o beijo** (cena `beijo`), com pétalas e corações.
     - **A pergunta engraçada** (cena `volta_casa`):
       > — Como é que a gente vai voltar pra casa?
       > — Gastei todo o dinheiro na passagem de ida.
       > — KAYO!
       > — E se a gente pedir carona pro Tatu Cristal? Ele rola rápido.
       > — Ele tá desmaiado ali no canto!
       > — Então a gente vai a pé até o mar e decide lá. Junto.
   - A última fala marca `fim_de_jogo`. O mundo volta ao título e **rola os créditos**.

## O Tatu Cristal

`data/enemies/tatu_cristal.tres`. O sprite vem da foto `assets/Chefe.png`, e a música é própria
(`tatu_cristal`).

| Golpe | Força | Animação (`fx`) |
|-------|-------|-----------------|
| Estilhaço de Cristal | 2 | espinhos de cristal rompem o chão, em linha, do tatu até o alvo |
| Raio Prismático | 4 | a luz se junta na boca dele e um raio de quatro cores cruza a tela |
| Rolada de Diamante | 3 | ele atravessa a tela inteira rolando, levantando poeira |
| Terremoto Cristalino | 1 | a tela treme cada vez mais forte e rachaduras correm pelo chão |
| Chuva de Cristais | 2 | cristais caem do escuro em cima do alvo, um depois do outro |
| Brilho Ofuscante | dorme 1 turno | as facetas brilham e a tela inteira fica branca |

- **A animação corre durante a preparação do golpe e chega no impacto**, que é o momento de apertar
  para defender. Ela é a deixa visual para o jogador.
- Para isso, o golpe passou a ser sorteado quando a preparação começa, e não no impacto. É o mesmo
  sorteio, na mesma quantidade, então nenhuma luta gravada mudou.
- A luta abre com o cartaz "O Tatu Cristal desperta!", o `intro` do próprio inimigo, sem treinador.
- **Difícil, mas sem exagero**, medido por `tests/unit/test_kayo_chefe.gd` em 12 sementes, com o
  Kayo **sozinho** no nível 3 (o máximo) e sem itens:
  - quem acerta todos os tempos vence sempre;
  - quem só aperta sem tempo perde sempre;
  - mesmo jogando perfeito, o Kayo fica abaixo da metade da vida em alguma semente;
  - com o Tatu e o Animal Louco capturados na fase 1, vence com folga.
- Entre os dois extremos estão as rapaduras (as da Obaachan e as da fase 1), a Água Sagrada e o
  descanso do Monge.
- **Dá para fugir** ("Pegar o beco"), como no Marcos. O template só aceita um chefe sem fuga por
  projeto, e esse lugar ainda é do Keeper do demo. Fugir não pula nada: ele continua no único vão
  do salão.

## Cenas animadas novas

Desenhadas por `game_kayo/tools/gerar_cenas.py` com os sprites do jogo.

| Cena | Onde | O que mostra |
|------|------|--------------|
| `tatu_desperta` | desafio | o Tatu Cristal no salão, com o casco brilhando, a aura pulsando e estilhaços em órbita |
| `cristal_quebra` | Isa presa | o cristal treme, racha, dá um clarão e explode; a Isa fica de pé, livre |
| `beijo` | conversa final | o abraço e depois o beijo no pátio à noite, com a lua, pétalas caindo e corações |
| `volta_casa` | conversa final | os dois de frente com um mapa aberto, pontos de interrogação e a gota de suor do Kayo |

## Créditos

- `data/credits/kayo_fim.json`, desenhados por `scripts/ui/ending_roll.gd` (novo).
- **"Um jogo de"**, com os nomes no dobro do tamanho: **Pedro Henrique, Carlos Eduardo, Kayo Andrade
  e Vinicius Fonseca**.
- Depois vêm o elenco, o chefe, as fases e com o que o jogo foi feito, e por fim "Obrigado por
  jogar!".
- **São animados**:
  - os nomes sobem pela tela e cada linha acende ao passar pelo meio e apaga nas bordas;
  - as estrelas piscam e as pétalas caem girando;
  - o Kayo e a Isa atravessam a tela andando, lá embaixo;
  - no fim, "FIM" aparece devagar com um coração batendo.
- A música é própria (`fim_da_jornada`). Um aperto no fim volta ao título.

## Mapas e arte

| Mapa | Tamanho | Destaques |
|------|---------|-----------|
| `jp_vila` | 22x12 | casas de shoji, lanternas de papel, bambu, cerejeiras, o torii, a lua |
| `jp_patio` | 20x14 | o castelo (6x5 tiles), o caminho de pedra, as lanternas, o lago das carpas, o Monge |
| `jp_salao` | 16x12 | tatame, pilares vermelhos, biombos, estandartes, taiko, a parede de cristal, a Isa presa |

- **Tiles novos**: 62, em `data/imports/tiles/lpc32/japao.png`, desenhados por
  `game_kayo/tools/gerar_tiles_japao.py`, com espelho de 16px no `gb16.json`.
  - **Chão**: piso do castelo, tatame, pedras do caminho, cascalho rastelado, muro do castelo,
    telhado, shoji, ponte laqueada, céu da noite e céu com lua.
  - **Jardim**: cerejeira, pétalas no chão, lanterna de pedra, bambu, pinheiro, lanterna de papel,
    cerca de bambu e placa.
  - **Salão**: pilar, biombo, estandarte, cristal, cristaizinhos no chão, vaso, taiko e katanas.
  - **Figuras grandes**: o torii (3x2) e o castelo (6x5).
- **Sprite novo**: `jp_isa_cristal`, a Isa dentro do prisma, desenhado por `tools/gerar_bichos.py`
  em cima do próprio sprite dela.
- **Músicas novas**, em `data/music`:
  - `castelo_sakura`: escala japonesa in-sen, lenta, com taiko;
  - `tatu_cristal`: frígio, com pedal de colcheias;
  - `fim_da_jornada`: dó maior, para os créditos.

## Flags da fase

| Flag | Quem marca | O que faz |
|------|-----------|-----------|
| `chegou_japao` | `japao_chegada` | a chegada não se repete |
| `ganhou_lanche` | escolha da Obaachan | as rapaduras saem uma vez só |
| `chegou_patio` | `patio_chegada` | a voz da Isa não se repete |
| `tatu_desafiou` | `tatu_desafio` | o desafio não se repete |
| (seen `jp_salao/tatu_cristal`) | a vitória | o chefe some; a Isa presa passa a abrir `cristal_quebra` |
| `isa_livre` | `cristal_quebra` | some a Isa presa, aparece a Isa livre |
| `fim_de_jogo` | `final_isa` | o manifesto rola os créditos (`ending_flag`) |

## Mudanças no código do template

Todas são opcionais por dado. Um jogo que não usa nada disso continua igual.

- **Animação por golpe do inimigo**
  - Um golpe pode ter `fx`: `shards`, `beam`, `rush`, `quake`, `storm` ou `flash`
    (`EnemyDef.MOVE_FX`). Um nome errado é recusado.
  - A `BattleLogic` sorteia o golpe quando a preparação abre e o expõe em `foe_move()`.
  - A `BattleFx.foe_move` desenha a animação no tempo da preparação.
  - A `BattleScreen` chama essa animação e faz o inimigo atravessar a tela no `rush`.
- **Cartaz de chefe sem treinador**: o `intro` do inimigo vale também quando não há treinador.
- **NPC que aparece e some por flag**
  - Um NPC no mapa pode ter `requires_flag` e `hidden_if_flag`.
  - A troca acontece no mesmo quadro em que a flag é marcada (`world_scene._sync_npcs`), e não só
    na próxima entrada no mapa.
- **O ar do mapa**
  - Um mapa pode ter `ambient`, com `tint` (a cor sobre o mundo inteiro, sem tocar nas janelas) e
    `petals` (`count`, `colors` e `fall`).
  - `AmbientLayer` (novo) desenha as pétalas por quadro de física, com semente.
  - As cores são dado, lidas por `AmbientColors`, na camada de dados.
  - O `MapData.problems` recusa cada erro pelo nome.
  - O campo sobrevive à ida e volta pelo Tiled e pelo LDtk.
- **Fim de jogo com créditos**
  - Campos novos no manifesto: `ending_flag` e `ending_roll`.
  - Quando uma conversa fecha com a flag marcada, o mundo volta ao título e abre a `EndingRoll`
    (nova).
  - O manifesto recusa um campo sem o outro, ou um arquivo de créditos com erro.
- **Testes novos**:
  - `tests/unit/test_kayo_chefe.gd`: o equilíbrio do chefe e o golpe sorteado na preparação;
  - `tests/unit/test_ending_roll.gd`: os créditos, que se mexem e ficam centralizados, e o
    `ambient`;
  - `tests/integration/test_world_npc_flags.gd`: a Isa presa e a Isa livre no salão de verdade.
- **Mutantes novos**: 7 em `tools/mutants.tsv`, e todos são pegos pelos testes.

## Validação

- **Sessão automática `jornada_completa.json`**: joga o jogo inteiro, do quarto do Kayo até o título
  depois dos créditos, em 777 passos.
  - O embarque, a vila e as rapaduras.
  - O torii, o pátio e o descanso do Monge.
  - A luta com o Tatu Cristal, vencida pelo `fight_well` em 1401 quadros.
  - O cristal quebrando, a conversa final, o beijo, a pergunta e os créditos rolando até o fim.
- **Resultado (29/10/2026)**: OK. `boots`, `fase1_completa` e `jornada_fase2` continuam OK.
- `compile_all` OK, `lint_rules` sem violações e `smoke_boot` OK. Os 1019 mutantes miram uma linha
  cada.
- Capturas de tela conferidas a olho: vila, pátio, desafio, luta, vitória, cristal quebrando, beijo,
  volta pra casa e créditos.

## Limitações

- **A luta permite fuga**, porque o template só aceita um chefe sem fuga e esse lugar é do demo.
  Tirar o demo libera isso.
- **O lago do pátio tem borda reta**: a água do LPC só desenha margem contra a grama, e o pátio é de
  cascalho.
- **Os créditos voltam ao título.** Quem carrega o último save volta para antes do fim (o jogo não
  salva sozinho).
- **Ao fechar o jogo nos créditos, o Godot avisa de um recurso ainda em uso**: a música dos créditos,
  que ainda está tocando. As sessões do demo que terminam no título mostram o mesmo aviso.
