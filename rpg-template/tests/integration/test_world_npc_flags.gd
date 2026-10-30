extends GdUnitTestSuite
## NPCs that come and go with a flag, through the real world scene: a record's `requires_flag`
## keeps it away until the flag is set, `hidden_if_flag` takes it away once it is, and the change
## lands the moment the flag does - the frame a conversation closes - not on the next visit.
##
## Played on the shipped Japan throne room, where the whole ending hangs off it: the Isa held in
## crystal and the Isa set free stand on the same tile, and exactly one of them may be there.

const GAME := "res://data/games/kayo.tres"

var _world: Node2D


func before_test() -> void:
	GameState.reset()


func after_test() -> void:
	if _world != null:
		_world.queue_free()
		_world = null


## Boots the game and walks straight into `map_id` with `flags` set. A new game starts from a
## clean state, so the flags are laid on AFTER it starts and the map is entered again over them.
func _boot_in(map_id: StringName, spawn: StringName, flags: Array[StringName] = []) -> void:
	var scene := load("res://scenes/world/world.tscn") as PackedScene
	_world = scene.instantiate() as Node2D
	add_child(_world)
	assert_bool(_world.start_game((load(GAME) as GameManifest).duplicate() as GameManifest)).is_true()
	# The opening scene would sit over the test, and the throne room's challenge too.
	for flag in flags + [&"acordou", &"tatu_desafiou", &"chegou_patio"]:
		GameState.set_flag(flag, true)
	Router.reset()
	assert_bool(_world.enter_map(map_id, spawn)).is_true()
	await get_tree().physics_frame


func test_the_held_isa_stands_until_the_flag_and_the_free_one_after() -> void:
	await _boot_in(&"jp_salao", &"entrada")
	var ids: Array[StringName] = _world.npc_ids()
	assert_array(ids).contains([&"isa_presa"])
	assert_array(ids).not_contains([&"isa"])
	_world._apply_effects([{"op": GameContext.OP_FLAG, "key": &"isa_livre", "value": true}])
	await get_tree().physics_frame
	ids = _world.npc_ids()
	assert_array(ids).contains([&"isa"])
	assert_array(ids).not_contains([&"isa_presa"])


func test_a_map_entered_with_the_flag_already_set_builds_only_the_free_one() -> void:
	await _boot_in(&"jp_salao", &"entrada", [&"isa_livre"])
	var ids: Array[StringName] = _world.npc_ids()
	assert_array(ids).contains([&"isa"])
	assert_array(ids).not_contains([&"isa_presa"])


func test_the_castle_maps_draw_their_air() -> void:
	await _boot_in(&"jp_patio", &"da_vila")
	var air: AmbientLayer = _world.ambient_layer()
	assert_object(air).override_failure_message("the courtyard drew no petals").is_not_null()
	assert_int(air.petal_count()).is_greater(0)
