class_name AmbientLayer
extends Node2D
## The air over a map: petals drifting down across the view, as `MapData.ambient` describes them.
##
## A VIEW and nothing else - nothing collides with a petal and nothing reads one, so a map plays the
## same with this layer gone. It lives in the map's own root, drawn over everything on it, and draws
## in SCREEN space turned back into the world each frame, so the petals fall across what the player
## sees wherever the camera has been clamped to. Counted in PHYSICS FRAMES and seeded from the map,
## never the clock, so a replayed session draws the same sky.
##
## Every colour comes from the map's data: a colour literal in scripts/world fails the build.

## Petals one tile tall drift this many tiles sideways at the top of their sway.
const SWAY_TILES := 0.4
## How much slower or faster than the stated fall one petal may be, as a fraction either way.
const FALL_SPREAD := 0.35

var _petals: Array[Dictionary] = []
var _colors: Array[Color] = []
var _fall_px := 0.0
var _tile := 16.0
var _rng: SeededRng = null
var _frame := 0


## Built from the map's `ambient.petals`, already checked by `MapData.problems`.
func setup(spec: Dictionary, tile_size: int, physics_fps: int, seed_value: int) -> void:
	z_index = RenderingServer.CANVAS_ITEM_Z_MAX - 1
	_tile = float(tile_size)
	_fall_px = float(spec.get("fall", 1.0)) * _tile / float(maxi(physics_fps, 1))
	for c: Variant in spec.get("colors", []):
		_colors.append(AmbientColors.of(c))
	_rng = SeededRng.new(seed_value)
	var view := _view_size()
	for i in int(spec.get("count", 0)):
		_petals.append(_new_petal(view, _rng.next_float(0.0, view.y)))


## How many petals are in the air: for a test, and for the session that wants to see them.
func petal_count() -> int:
	return _petals.size()


func _physics_process(_delta: float) -> void:
	_frame += 1
	var view := _view_size()
	for petal in _petals:
		petal["y"] = float(petal["y"]) + float(petal["speed"])
		if float(petal["y"]) > view.y + 4.0:
			petal.merge(_new_petal(view, -4.0), true)
	queue_redraw()


func _draw() -> void:
	var to_world := get_viewport().get_canvas_transform().affine_inverse()
	var local := get_global_transform().affine_inverse()
	for petal in _petals:
		var phase := float(_frame) * float(petal["spin"]) + float(petal["phase"])
		var sway := sin(phase) * SWAY_TILES * _tile * 0.5
		var on_screen := Vector2(float(petal["x"]) + sway, float(petal["y"]))
		var at := local * (to_world * on_screen)
		# Tumbling: the petal shows its face, then its edge, as it turns.
		var wide := 1.0 + 2.0 * absf(cos(phase))
		draw_rect(Rect2(at, Vector2(wide, 2.0)), _colors[int(petal["color"])])


func _new_petal(view: Vector2, y: float) -> Dictionary:
	return {
		"x": _rng.next_float(0.0, view.x),
		"y": y,
		"speed": _fall_px * _rng.next_float(1.0 - FALL_SPREAD, 1.0 + FALL_SPREAD),
		"spin": _rng.next_float(0.03, 0.08),
		"phase": _rng.next_float(0.0, TAU),
		"color": _rng.next_int(0, maxi(_colors.size() - 1, 0)),
	}


func _view_size() -> Vector2:
	return get_viewport_rect().size if is_inside_tree() else Vector2(UiScale.DESIGN_SIZE)
