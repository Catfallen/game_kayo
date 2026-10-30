# A Jornada do Kayo

Um jogo de plataforma/RPG 2D feito em Godot 4, desenvolvido como projeto de faculdade em duas sessões utilizando 100% Claude Opus 5.5.

---

## A História

Kayo nasceu em Açailândia no Maranhão, mudou pro Pará antes de aprender a andar, voltou pro Maranhão, foi pro Mato Grosso do Sul com 18 anos — e foi lá que conheceu Isa, uma japonesa que morava na mesma cidade.

Relacionamento saudável, sem brigas, tudo certo. Até ela precisar voltar pro Japão.

Kayo viu ela ir. Pela janela do aeroporto, viu o avião partir com ela dentro. E o Google Maps só mostrava um oceano inteiro no caminho.

Algum tempo depois chegou uma mensagem: ela estava presa num castelo, com um chefão impedindo a saída. Qualquer pessoa normal perguntaria se ela estava bem. Kayo perguntou — mas já estava olhando o poste no fundo da foto, tentando localizar onde ficava o castelo.

É campeão no GeoGuessr. Acertou.

Agora ele precisa atravessar de volta todos os lugares onde viveu — Nordeste, Norte, Maranhão, Mato Grosso do Sul — até chegar ao Japão e enfrentar o chefão. Sem treinamento, sem dinheiro sobrando, e com a confiança de quem já ganhou round impossível de CS sozinho.

> *"Enquanto isso ela tá no castelo esperando o resgate, tomara que esteja esperando mesmo."*

---

## Gameplay

- Plataforma/RPG 2D com visão lateral
- Fases baseadas nos lugares onde Kayo viveu
- Inimigos temáticos por região (tatu, animal louco, etc.)
- Boss final no castelo no Japão
- Personagens: Kayo, Isa, Chefe

---

## Personagens

| Personagem | Descrição |
|---|---|
| **Kayo** | Protagonista. Campeão no GeoGuessr, veterano de CS e LoL, nunca planejou a viagem de volta |
| **Isa** | A princesa. Japonesa, presa num castelo, esperando o resgate (espero que ainda esteja esperando) |
| **Chefe** | O antagonista. Mora num castelo. Cometeu o erro de deixar aparecer um poste na foto |

---

## Tecnologia

- **Engine:** [Godot 4](https://godotengine.org/)
- **Base:** [rpg-template](https://github.com/Ali0600/rpg-template) — template 2D RPG reutilizável para Godot 4.7
- **Arte:** Sprites customizados desenhados para o jogo
- **IA:** Desenvolvido com **Claude Opus 5.5** (duas sessões completas, 100% do modelo)

---

## Como rodar

```bash
# Abrir no Godot 4.7+
/Applications/Godot.app/Contents/MacOS/Godot --path rpg-template
```

No Windows, abrir o projeto `rpg-template/project.godot` diretamente no Godot Editor.

---

## Estrutura do Projeto

```
game_kayo/
├── assets/          # Sprites dos personagens (Kayo, Isa, Chefe, inimigos)
├── rpg-template/    # Engine do jogo baseada no rpg-template
│   ├── data/        # Mapas, diálogos, itens, inimigos (tudo como dados)
│   ├── scripts/     # Sistemas: movimento, combate, saves, UI
│   └── games/       # Código específico do jogo "A Jornada do Kayo"
└── message.txt      # A história original do Kayo (vale a leitura)
```

---

## Desenvolvimento

Este jogo foi construído em duas sessões de Claude Opus 5.5 como projeto de faculdade. O template base (`rpg-template`) permite criar um RPG completo editando apenas dados — mapas, diálogos, inimigos e itens — sem precisar mexer no código do engine.

A história veio do próprio Kayo. O `message.txt` na raiz do projeto conta tudo em primeira pessoa, do jeito que ele escreve.

---

*"Se ele queria esconder alguém tinha que ter fechado a cortina antes da foto, deixou aparecer meio poste pra um champion agora aguenta."*
