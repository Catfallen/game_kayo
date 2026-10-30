extends GdUnitTestSuite
## O Tatu Cristal, chefe final de A Jornada do Kayo, jogado de verdade: a BattleLogic real, o
## chefe do arquivo e o Kayo no nivel do fim do jogo, em doze sementes, pelos pilotos do template.
##
## "Dificil mas sem escaralhar" e dito aqui como duas metades, a forma que o test_battle_content
## usa para o Keeper: quem acerta todo tempo vence SEMPRE, mesmo sozinho; quem nao acerta tempo
## nenhum perde SEMPRE, mesmo no nivel maximo. O Kayo luta sozinho no pior caso porque os parceiros
## sao capturas opcionais da fase 1 - o chefe tem que ser vencivel sem eles.

const KAYO := "res://data/games/kayo.tres"
const CHEFE := "res://data/enemies/tatu_cristal.tres"
const SEEDS := 12


func _luta(seed_value: int, parceiros: bool) -> BattleLogic:
	var manifest := load(KAYO) as GameManifest
	var top := manifest.combat.xp_curve.size() + 1
	var members: Array = manifest.party if parceiros else []
	return BattleLogic.of(manifest.combat, [load(CHEFE) as EnemyDef],
		BattleHelpers.party_of(manifest, members, top), [], "jp_salao/tatu_cristal", seed_value)


func test_o_chefe_e_vencido_por_quem_acerta_o_tempo_mesmo_sozinho() -> void:
	for seed_value in range(1, SEEDS + 1):
		var report := BattleDriver.play(_luta(seed_value, false), BattleDriver.Policy.PERFECT)
		assert_str(report.fault).is_empty()
		assert_bool(report.ended).is_true()
		assert_int(report.outcome).override_failure_message(
			"o Kayo acertando tudo PERDE do Tatu Cristal na semente %d (%s)" % [seed_value, report.party_hp]
		).is_equal(BattleLogic.Outcome.VICTORY)


func test_o_chefe_vence_quem_so_aperta_sem_tempo() -> void:
	for seed_value in range(1, SEEDS + 1):
		var report := BattleDriver.play(_luta(seed_value, false), BattleDriver.Policy.MASH)
		assert_bool(report.ended).is_true()
		assert_int(report.outcome).override_failure_message(
			"quem nao acerta tempo nenhum vence o Tatu Cristal na semente %d - ele nao e chefe" % seed_value
		).is_equal(BattleLogic.Outcome.DEFEAT)


func test_mesmo_acertando_tudo_o_chefe_machuca() -> void:
	# A outra metade do "dificil": um chefe que o jogador perfeito vence sem perder vida nao
	# exige nada. Em alguma semente o Kayo tem que terminar com menos da metade.
	var manifest := load(KAYO) as GameManifest
	var full := manifest.combat.max_hp(manifest.combat.xp_curve.size() + 1)
	var lowest := full
	for seed_value in range(1, SEEDS + 1):
		var report := BattleDriver.play(_luta(seed_value, false), BattleDriver.Policy.PERFECT)
		lowest = mini(lowest, report.party_hp[0])
	assert_int(lowest).override_failure_message(
		"o Kayo perfeito nunca ficou abaixo de %d de %d - o chefe nao assusta" % [lowest, full]
	).is_less(full / 2)


func test_com_os_parceiros_a_luta_continua_vencivel() -> void:
	for seed_value in range(1, SEEDS + 1):
		var report := BattleDriver.play(_luta(seed_value, true), BattleDriver.Policy.PERFECT)
		assert_int(report.outcome).is_equal(BattleLogic.Outcome.VICTORY)


func test_cada_golpe_do_chefe_tem_animacao_e_ela_e_conhecida() -> void:
	var chefe := load(CHEFE) as EnemyDef
	assert_array(chefe.problems()).is_empty()
	var vistos := {}
	for move: Dictionary in chefe.moves:
		var fx := str(move.get("fx", ""))
		assert_bool(EnemyDef.MOVE_FX.has(fx)).override_failure_message(
			"o golpe '%s' nao tem animacao conhecida ('%s')" % [move.get("name", ""), fx]).is_true()
		vistos[fx] = true
	assert_int(vistos.size()).override_failure_message(
		"dois golpes do chefe desenham a mesma coisa").is_equal(chefe.moves.size())


func test_um_efeito_desconhecido_e_recusado_pelo_nome() -> void:
	var def := EnemyDef.new()
	def.id = &"x"
	def.name = "X"
	def.moves = [{"name": "Golpe", "power": 1, "fx": "fogos"}]
	assert_str("\n".join(def.problems())).contains("draws 'fogos'")


func test_o_golpe_e_sorteado_quando_a_preparacao_comeca() -> void:
	# A tela anima o golpe DURANTE a preparacao, entao ele precisa estar escolhido quando ela abre,
	# e o impacto tem que usar esse mesmo golpe - em todos os turnos, nao so no primeiro: com seis
	# golpes, um segundo sorteio no impacto acerta o mesmo por acaso de vez em quando.
	var logic := _luta(3, false)
	var turnos := 0
	var frames := 0
	while turnos < 8 and not logic.finished() and frames < 60000:
		frames += 1
		if logic.phase() == BattleLogic.Phase.MENU:
			logic.press()
		if logic.phase() != BattleLogic.Phase.ENEMY_ACT:
			logic.tick()
			continue
		var chosen := str(logic.foe_move().get("name", ""))
		assert_str(chosen).is_not_empty()
		while logic.phase() == BattleLogic.Phase.ENEMY_ACT:
			logic.tick()
		assert_str(logic.message()).override_failure_message(
			"a preparacao mostrou '%s' e o impacto disse: %s" % [chosen, logic.message()]).contains(chosen)
		turnos += 1
	# Quem so aperta Ataque cai em uns cinco turnos; quatro ja bastam para o acaso nao explicar.
	assert_int(turnos).is_greater_equal(4)
