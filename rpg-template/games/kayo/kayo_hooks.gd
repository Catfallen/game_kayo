extends GameHooks
## A Jornada do Kayo: o que os dados sozinhos não sabem fazer.
##
## Cenas que abrem sozinhas na primeira entrada de um mapa, as três pistas de GeoGuessr que
## juntas abrem a estrada, o pote que dá três rapaduras de uma vez e o Marcos depois da luta.
##
## Fase 2 (Três Lagoas): a Isa entra na equipe ao chegar (GameManifest.companion, pela flag
## isa_junto), a conversa com ela muda com o mapa, o banco da Lagoa só conta a notícia depois do
## tereré, e o portão e o janelão do aeroporto fecham a fase.
##
## Fase 3 (Japão): uma cena na primeira entrada de cada mapa do castelo, e a Isa presa no cristal,
## que só se quebra depois que o Tatu Cristal cai. O resto do fim é dado: a Isa livre aparece por
## requires_flag, a conversa final marca fim_de_jogo e o manifesto rola os créditos.

const MAP_CASA := &"kayo_casa"
const MAP_ESTRADA := &"kayo_estrada"
const MAP_TERREIRO := &"kayo_terreiro"

const FLAG_ACORDOU := &"acordou"
const FLAG_ESTRADA := &"leu_a_estrada"
const FLAG_DESAFIO := &"marcos_desafiou"
const FLAG_PISTAS := &"pistas_nordeste"

## Id do objeto no mapa = id do diálogo = flag marcada ao examinar.
const PISTAS: Array[StringName] = [&"pista_poste", &"pista_placa", &"pista_mandacaru"]

const POTE := &"pote_rapadura"
const POTE_VAZIO := &"pote_vazio"
const SEEN_POTE := "kayo_casa/pote_rapadura"
const RAPADURA := &"rapadura"
const RAPADURAS_NO_POTE := 3

## As Cuiabolas do avô, em cima da mesa: cinco de uma vez, como o pote.
const CUIABOLAS := &"cuiabolas"
const CUIABOLAS_VAZIO := &"cuiabolas_vazio"
const SEEN_CUIABOLAS := "kayo_casa/cuiabolas"
const CUIABOLA := &"cuiabola"
const CUIABOLAS_NA_MESA := 5

const MARCOS := &"marcos"
const SEEN_BICHOS := "kayo_terreiro/bichos_marcos"

const MAP_RODOVIARIA := &"tl_rodoviaria"
const MAP_LAGOA := &"tl_lagoa"
const MAP_AEROPORTO := &"tl_aeroporto"
## Marcada pelos hooks ao chegar, antes da conversa abrir: é o que faz a Isa aparecer no spawn
## `companion` e andar atrás do Kayo (data/games/kayo.tres).
const FLAG_ISA_JUNTO := &"isa_junto"
const FLAG_CHEGOU := &"chegou_tl"
const FLAG_AEROPORTO := &"aeroporto_chegou"
const FLAG_TERERE := &"tomou_terere"
const FLAG_VIAGEM := &"sabe_da_viagem"
const FLAG_EMBARCOU := &"isa_embarcou"
const FLAG_FASE2 := &"fase2_completa"

## A conversa com a Isa em cada mapa (o alvo `companion`). Na Lagoa, depois da notícia, outra.
const CONVERSA_ISA := {
	&"tl_rodoviaria": &"isa_rodoviaria",
	&"tl_centro": &"isa_centro",
	&"tl_lagoa": &"isa_lagoa",
	&"tl_aeroporto": &"isa_aeroporto",
}
const CONVERSA_ISA_TRISTE := &"isa_lagoa_triste"

const MAP_VILA := &"jp_vila"
const MAP_PATIO := &"jp_patio"
const MAP_SALAO := &"jp_salao"
const FLAG_JAPAO := &"chegou_japao"
const FLAG_PATIO := &"chegou_patio"
const FLAG_TATU := &"tatu_desafiou"
## O Tatu Cristal vencido: a chave "seen" do registro dele no salão, como a do Marcos.
const SEEN_TATU := "jp_salao/tatu_cristal"
const ISA_PRESA := &"isa_presa"

const BANCO_LAGOA := &"banco_lagoa"
const PORTAO := &"portao_embarque"
const JANELA := &"janela"


func on_map_entered(ctx: GameContext) -> void:
	if ctx.map_id == MAP_CASA and not ctx.has_flag(FLAG_ACORDOU):
		ctx.say(&"intro_casa")
	elif ctx.map_id == MAP_ESTRADA and not ctx.has_flag(FLAG_ESTRADA):
		ctx.say(&"estrada_conclusao")
	elif ctx.map_id == MAP_TERREIRO and not ctx.has_flag(FLAG_DESAFIO):
		ctx.say(&"marcos_desafio")
	elif ctx.map_id == MAP_RODOVIARIA and not ctx.has_flag(FLAG_CHEGOU):
		ctx.set_flag(FLAG_ISA_JUNTO)
		ctx.say(&"chegada_isa")
	elif ctx.map_id == MAP_AEROPORTO and not ctx.has_flag(FLAG_AEROPORTO):
		ctx.say(&"aeroporto_chegada")
	elif ctx.map_id == MAP_VILA and not ctx.has_flag(FLAG_JAPAO):
		ctx.say(&"japao_chegada")
	elif ctx.map_id == MAP_PATIO and not ctx.has_flag(FLAG_PATIO):
		ctx.say(&"patio_chegada")
	elif ctx.map_id == MAP_SALAO and not ctx.has_flag(FLAG_TATU) and not ctx.was_seen(SEEN_TATU):
		ctx.say(&"tatu_desafio")


func on_interact(ctx: GameContext, target: Interactor.Target) -> bool:
	if PISTAS.has(target.id):
		ctx.say(target.id)
		ctx.set_flag(target.id)
		var found := 1
		for pista in PISTAS:
			if pista != target.id and ctx.has_flag(pista):
				found += 1
		if found == PISTAS.size():
			ctx.set_flag(FLAG_PISTAS)
		return true
	if target.id == POTE:
		if ctx.was_seen(SEEN_POTE):
			ctx.say(POTE_VAZIO)
		else:
			ctx.say(POTE)
			ctx.give_item(RAPADURA, RAPADURAS_NO_POTE)
			ctx.mark_seen(SEEN_POTE)
		return true
	if target.id == CUIABOLAS:
		if ctx.was_seen(SEEN_CUIABOLAS):
			ctx.say(CUIABOLAS_VAZIO)
		else:
			ctx.say(CUIABOLAS)
			ctx.give_item(CUIABOLA, CUIABOLAS_NA_MESA)
			ctx.mark_seen(SEEN_CUIABOLAS)
		return true
	if target.id == MARCOS and ctx.was_seen(SEEN_BICHOS):
		ctx.say(&"marcos_derrotado")
		return true
	if target.id == GameHooks.COMPANION and CONVERSA_ISA.has(ctx.map_id):
		if ctx.map_id == MAP_LAGOA and ctx.has_flag(FLAG_VIAGEM):
			ctx.say(CONVERSA_ISA_TRISTE)
		else:
			ctx.say(StringName(CONVERSA_ISA[ctx.map_id]))
		return true
	if target.id == BANCO_LAGOA:
		if not ctx.has_flag(FLAG_TERERE):
			ctx.say(&"banco_sem_terere")
		elif not ctx.has_flag(FLAG_VIAGEM):
			ctx.say(&"por_do_sol")
		else:
			ctx.say(&"banco_lagoa_depois")
		return true
	if target.id == PORTAO:
		ctx.say(&"portao_vazio" if ctx.has_flag(FLAG_EMBARCOU) else &"despedida")
		return true
	if target.id == ISA_PRESA and ctx.was_seen(SEEN_TATU):
		ctx.say(&"cristal_quebra")
		return true
	if target.id == JANELA:
		if not ctx.has_flag(FLAG_EMBARCOU):
			ctx.say(&"janela_antes")
		elif not ctx.has_flag(FLAG_FASE2):
			ctx.say(&"janela_aviao")
		else:
			ctx.say(&"janela_depois")
		return true
	return false


func dialog_ids() -> Array[StringName]:
	return [&"intro_casa", &"estrada_conclusao", &"marcos_desafio", &"marcos_derrotado", POTE_VAZIO,
		CUIABOLAS_VAZIO,
		&"chegada_isa", &"aeroporto_chegada", &"isa_rodoviaria", &"isa_centro", &"isa_lagoa",
		CONVERSA_ISA_TRISTE, &"isa_aeroporto", &"por_do_sol", &"banco_lagoa_depois", &"despedida",
		&"janela_aviao", &"janela_depois",
		&"japao_chegada", &"patio_chegada", &"tatu_desafio", &"cristal_quebra"]
