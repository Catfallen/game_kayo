# Fase 2: Três Lagoas (Mato Grosso do Sul)

O Kayo desce do ônibus que veio do Maranhão e a Isa está esperando. A fase não tem combate. Os dois
passeiam pela cidade com a Isa andando atrás do Kayo: conversam, se abraçam e tomam tereré na
barraca da Lagoa Maior. No banco da beira da Lagoa, ela conta que vai voltar para o Japão. No
aeroporto vem a despedida, com o abraço apertado, e depois o avião indo embora pela janela.

Pedido do dono e plano geral: [PLANO.md](PLANO.md).

## Roteiro

1. **Rodoviária** (`tl_rodoviaria`)
   - Chega-se pela estrada a leste do terreiro do Marcos. Ela só abre depois de ler a placa do ponto,
     que marca `fase1_completa`.
   - Na primeira entrada os hooks marcam `isa_junto` e abrem `chegada_isa`.
   - A Isa aparece no spawn `companion`, corre até o Kayo e os dois se abraçam (cena
     `abraco_chegada`, com corações).
   - Uma dica avisa que dá para falar com ela. Daqui em diante ela anda atrás do Kayo.
2. **Praça do centro** (`tl_centro`)
   - Ipês, coqueiros, bancos, carrinho de picolé e o letreiro da cidade.
   - Moradores com falas locais: o calor de 40 graus e a "capital mundial da celulose".
3. **Lagoa Maior** (`tl_lagoa`)
   - A lagoa com margem, calçadão de bloquete, ipês e capivaras andando.
   - **Barraca de tereré**: a barraca e o Seu Zé abrem `terere`. Na primeira rodada ("Dois! Um pra mim
     e um pra ela") ele explica que tereré se toma junto, numa guampa só, e a cena `terere` mostra os
     dois passando a guampa. Isso marca `tomou_terere`. Depois dá para pedir mais rodadas.
   - **Banco da beira da Lagoa**: antes do tereré, a Isa pede o tereré primeiro. Depois dele, abre
     `por_do_sol`: os dois de costas, o sol descendo na Lagoa e a Isa encostando no ombro dele. Ela
     conta que a família vai voltar para o Japão e que o voo é amanhã. Isso marca `sabe_da_viagem`.
   - O caminho do aeroporto (leste) fica trancado até lá ("Hoje não, Kayo. Fica aqui comigo na Lagoa").
4. **Aeroporto** (`tl_aeroporto`)
   - A chegada abre `aeroporto_chegada`.
   - **Portão 1**: abre a `despedida`, a conversa triste ("Eu te amo. Do Maranhão até o Japão. O
     caminho inteiro."). O jogador escolhe "Abraçar a Isa bem forte" e a cena `abraco_despedida`
     segue por cinco falas, com lágrimas. Depois `isa_embarcou` tira a Isa de trás do Kayo.
   - **Janelão**: a cena `aviao`, com o avião correndo na pista, subindo e sumindo. Ela termina
     com "acertar o Japão no mapa não te leva até lá" e marca `fase2_completa`.
   - A última fala ("Alguns dias depois, chega uma mensagem muito estranha da Isa...") é a ponte para
     o Japão. Na mesma conversa chega a mensagem dela presa no castelo, e a porta da direita do
     saguão (17,6), o embarque internacional, abre para a fase 3 ([FASE_3_JAPAO.md](FASE_3_JAPAO.md)).

## A Isa acompanhando o Kayo

- Ela anda **atrás do Kayo**, refazendo o caminho dele com um tile de atraso, como um Pokémon que
  segue o treinador ou a fila de EarthBound. Ela não tem colisão, então nunca prende o Kayo num
  corredor.
- **Conversar com ela**: perto dela, apertar o botão de interagir abre a conversa do mapa, com três
  escolhas: **Conversar**, **Abraçar a Isa** (cena `abraco`) ou **Nada não**.
  - Há uma conversa por mapa: `isa_rodoviaria`, `isa_centro`, `isa_lagoa` e `isa_aeroporto`.
  - Na Lagoa, depois da notícia, a conversa vira `isa_lagoa_triste`.
- Ela entra com `isa_junto` e sai com `isa_embarcou`, ambas configuradas no manifesto. Como tudo vem
  de flags, o save não precisou mudar.

## Cenas animadas

Desenhadas por `game_kayo/tools/gerar_cenas.py` com os próprios sprites do jogo. Ficam em
`assets/kayo/cenas/`, uma tira PNG mais um `.json` com quadros, tempo de cada quadro e o quadro onde
a repetição recomeça.

| Cena | Onde | O que mostra |
|------|------|--------------|
| `abraco_chegada` | rodoviária | os dois correm um para o outro e se abraçam, com corações (close) |
| `abraco` | conversa com a Isa | o mesmo abraço, num fundo rosa |
| `terere` | barraca | a guampa passando do Kayo para a Isa, cada um tomando (close) |
| `por_do_sol` | banco da Lagoa | os dois de costas, o sol descendo, a Isa encostando no ombro dele |
| `abraco_despedida` | portão 1 | o abraço apertado, devagar, com lágrimas e um coração pulsando |
| `aviao` | janelão | o avião correndo, decolando e sumindo; o Kayo olhando de costas |

## Mapas

| Mapa | Tamanho | Destaques |
|------|---------|-----------|
| `tl_rodoviaria` | 18x11 | prédio da rodoviária, o ônibus, orelhão, carro, ipês |
| `tl_centro` | 20x13 | praça com ipês, coqueiros, bancos, picolé, letreiro, 2 moradores |
| `tl_lagoa` | 22x14 | a Lagoa Maior, o calçadão, a barraca de tereré, o Seu Zé, 2 capivaras |
| `tl_aeroporto` | 18x11 | check-in, painel de voos, cadeiras, portão 1, janelão, 3 pessoas |

- **Tiles novos**: 32, em `data/imports/tiles/lpc32/cidade.png`, desenhados por
  `game_kayo/tools/gerar_tiles_cidade.py`. São asfalto, faixa, calçada, calçadão, reboco, piso de
  aeroporto, vidro, porta de vidro, ipê amarelo e rosa, coqueiro, poste, banco de praça, lixeira,
  flores, letreiro, barraca de tereré (2 tiles), ônibus (6x3 tiles), carro (2x1 tiles), placa da rodoviária,
  orelhão, carrinho de picolé, balcão, cadeiras, painel de voos, vaso, portão, mala, bebedouro e
  placa de saguão.
- **A água da Lagoa** é a do LPC, que já desenha a margem sozinha.
- **Bicho novo**: a capivara (`tl_capivara`), desenhada por `tools/gerar_bichos.py`.

## Flags da fase

| Flag | Quem marca | O que faz |
|------|-----------|-----------|
| `isa_junto` | hooks, ao chegar na rodoviária | a Isa passa a andar atrás do Kayo |
| `chegou_tl` | `chegada_isa` | a chegada não se repete |
| `tomou_terere` | escolha na barraca | o banco da Lagoa passa a contar a notícia |
| `sabe_da_viagem` | `por_do_sol` | abre o caminho do aeroporto |
| `aeroporto_chegou` | `aeroporto_chegada` | a chegada não se repete |
| `isa_embarcou` | `despedida` | a Isa sai de trás do Kayo; o janelão mostra o avião |
| `fase2_completa` | `janela_aviao` | fim da fase 2 |

## Mudanças no código do template

Todas são opcionais por dado. Um jogo que não usa nada disso continua igual.

- **Companheiro que segue o jogador**
  - `GameManifest`: os campos `companion`, `companion_flag` e `companion_gone_flag`.
  - `world_scene.gd`: o rastro de posições, a Isa desenhada sem corpo, e a conversa com ela pelo
    alvo `GameHooks.COMPANION`.
  - Quando ela entra no meio de um mapa, aparece no spawn `companion`.
- **Cenas nos diálogos**
  - Um nó de diálogo pode ter `scene` (um PNG em tira).
  - `DialogScene` (`scripts/ui/dialog_scene.gd`, novo) toca a tira contando quadros de física, e a
    `DialogBox` mostra a cena numa moldura acima da caixa.
  - O `problems()` do `DialogRunner` recusa uma cena que não existe ou que tem o `.json` errado.
- **Teste novo**: `tests/unit/test_dialog_scene.gd`.

## Validação

- **Sessão automática `jornada_fase2.json`**: joga a fase 1 inteira e depois a fase 2 inteira.
  - A chegada com o abraço.
  - Falar com a Isa na rodoviária e no aeroporto.
  - O banco e o aeroporto recusando antes da hora.
  - O tereré, o pôr do sol, a despedida com o abraço e o avião.
- **Resultado (29/10/2026)**: OK, 537 passos. `fase1_completa.json` e `boots.json` também passam.
- `compile_all` OK, `lint_rules` sem violações e `smoke_boot` OK. Os 1012 mutantes continuam
  mirando uma linha cada.
- **Suíte do template**: 1794 casos. Restam as mesmas 5 falhas em 2 testes de antes, nenhum ligado à
  fase: `test_title` (dois jogos no projeto) e `test_ci_paths` (`sha512sum` no Windows).
- As capturas de tela de cada cena foram conferidas a olho.

## Limitações

- **A Isa não tem colisão**, de propósito, então às vezes ela passa por cima de um banco ou de uma planta.
- **A Isa só fala quando está perto do Kayo**, até um tile e meio. Logo depois de chegar ela ainda
  está correndo até ele.
- **As cenas são feitas com os sprites do próprio jogo**, que vieram de uma foto só: o abraço é um
  close dos dois juntos, não uma arte desenhada à mão.
