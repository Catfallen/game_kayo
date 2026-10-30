class_name EndingRoll
extends CanvasLayer
## The credits that roll after a game's ending, drawn: the staff rising up a dark screen while
## petals fall and stars blink, the cast walking along the bottom, and "the end" settling last.
##
## Where the title's Credits row is a DOCUMENT - who drew the art, paged, no motion, because a
## licence asks for it - this is the genre's other credits: the staff roll after the ending, which
## every reference plays as a sequence rather than a page. What it says is a GAME's data
## (`GameManifest.ending_roll`, a JSON file read by `read()`); this paints it and reports.
##
## Counted in PHYSICS FRAMES like every screen here, so a scripted session sees the same roll on
## every machine. Every colour is a ROLE off the style, because a colour literal in scripts/ui
## fails the build. It never closes itself: once the roll has finished a press asks to leave and
## the world, which opened it, decides what comes next.

signal sound_wanted(id: StringName)
signal left

## Over the title (30), which is where the world opens it, and over the licence credits (35).
const LAYER := 36
const ROW_PITCH := 12
const HEADING_GAP := 6
const BLOCK_GAP := 26
## Headings and the closing line are drawn at twice the font: a pixel font scaled by a whole
## number stays sharp, and a staff roll needs a size above the names to read as one.
const BIG := 2
const STARS := 28
const PETALS := 34
## Every key a roll file may carry. Closed, so a typo is a refusal rather than a line nobody sees.
const KEYS := ["_readme", "title", "blocks", "last", "parade", "speed", "music"]

var _style: SpriteStyle = null
var _size := Vector2.ZERO
var _backdrop := ColorRect.new()
## Everything that scrolls, as one node moved up a little every frame.
var _scroll := Control.new()
var _scroll_end := 0.0
var _speed := 0.4
var _rows: Array[Label] = []
var _last: Label = null
var _heart: Label = null
var _parade: Array[SpriteView] = []
var _stars: Array[ColorRect] = []
var _petals: Array[ColorRect] = []
var _petal_state: Array[Vector3] = []
var _rng: SeededRng = null
var _frame := 0
var _done := false
## The frame "the end" arrived on, so its fade and the heart's beat count from there.
var _done_frame := -1
var _committed := false
var _gate := InputGate.new()


## The roll file as a Dictionary, or empty when it cannot be read. The world reads it and hands it
## in, because where a game keeps its words is a question about the running game.
static func read(path: String) -> Dictionary:
	var file := JsonFile.read(path)
	return file.data if file.ok else {}


## Everything wrong with the roll file at `path`, for the manifest's own problems().
static func problems_of(path: String) -> Array[String]:
	var out: Array[String] = []
	var file := JsonFile.read(path)
	if not file.ok:
		out.append("ending roll '%s' does not load: %s" % [path, file.error])
		return out
	var data := file.data
	for key: Variant in data:
		if not KEYS.has(str(key)):
			out.append("ending roll '%s' has '%s', which is not one of %s" % [path, key, KEYS])
	var blocks: Variant = data.get("blocks", [])
	if not blocks is Array or (blocks as Array).is_empty():
		out.append("ending roll '%s' has no blocks - nobody would be credited" % path)
		return out
	for i in (blocks as Array).size():
		var block: Variant = (blocks as Array)[i]
		if not block is Dictionary or str((block as Dictionary).get("heading", "")).is_empty():
			out.append("ending roll '%s' block %d has no heading" % [path, i])
			continue
		var names: Variant = (block as Dictionary).get("names", [])
		if not names is Array or (names as Array).is_empty():
			out.append("ending roll '%s' block %d names nobody" % [path, i])
	var speed: Variant = data.get("speed", 0.4)
	if (typeof(speed) != TYPE_INT and typeof(speed) != TYPE_FLOAT) or float(speed) <= 0.0:
		out.append("ending roll '%s' scrolls at %s - it would never move" % [path, speed])
	return out


func _ready() -> void:
	layer = LAYER


## `source` draws the parade; null draws none (a test with no art, or a style with no sheets).
func setup(roll: Dictionary, style: SpriteStyle, viewport_size: Vector2i, source: SpriteSource,
		seed_value: int) -> void:
	_style = style
	_size = Vector2(viewport_size)
	_speed = float(roll.get("speed", 0.4))
	_rng = SeededRng.new(seed_value)
	_backdrop.size = _size
	_backdrop.color = _style.ui_color("panel")
	add_child(_backdrop)
	_build_sky()
	add_child(_scroll)
	_build_rows(roll)
	_build_parade(roll, source)
	_build_last(roll)
	_paint()


## True once "the end" is on screen and a press will leave. For tests and play sessions.
func finished() -> bool:
	return _done


## How far the staff has risen, in design pixels. For tests.
func scrolled() -> float:
	return -_scroll.position.y


func _build_sky() -> void:
	for i in STARS:
		var star := _dot(Vector2(1.0, 1.0), "dim" if i % 3 else "text")
		star.position = Vector2(_rng.next_float(0.0, _size.x), _rng.next_float(0.0, _size.y * 0.8))
		_stars.append(star)
	for i in PETALS:
		var petal := _dot(Vector2(2.0, 1.0), "hp" if i % 2 else "select")
		_petals.append(petal)
		# x, y, phase
		_petal_state.append(Vector3(_rng.next_float(0.0, _size.x), _rng.next_float(-_size.y, _size.y),
			_rng.next_float(0.0, TAU)))


func _build_rows(roll: Dictionary) -> void:
	var y := _size.y + 8.0
	var title := str(roll.get("title", ""))
	if not title.is_empty():
		y = _row(title.to_upper(), "select", y, BIG) + BLOCK_GAP
	for entry: Variant in roll.get("blocks", []):
		var block: Dictionary = entry
		y = _row(str(block.get("heading", "")), "dim", y, 1) + HEADING_GAP
		for named: Variant in block.get("names", []):
			y = _row(str(named), "text", y, BIG if bool(block.get("big", false)) else 1)
		y += BLOCK_GAP
	_scroll_end = y - _size.y * 0.5


func _row(text: String, role: String, y: float, scale: int) -> float:
	var label := UiChrome.label(_style, role)
	label.text = text
	label.add_theme_color_override("font_outline_color", _style.ui_color("panel"))
	label.add_theme_constant_override("outline_size", 2)
	_scroll.add_child(label)
	_centre(label, y, scale)
	_rows.append(label)
	return y + float(ROW_PITCH * scale)


func _build_parade(roll: Dictionary, source: SpriteSource) -> void:
	if source == null:
		return
	var cast: Array = roll.get("parade", [])
	for i in cast.size():
		var view := SpriteView.new()
		if not view.apply_source(source, StringName(str(cast[i]))):
			view.free()
			continue
		add_child(view)
		var drawn := FightScreen.fighter_scale(_style)
		view.scale = Vector2(drawn, drawn)
		view.set_pose(&"walk", Dir.D.RIGHT)
		_parade.append(view)


func _build_last(roll: Dictionary) -> void:
	_last = UiChrome.label(_style, "text")
	_last.text = str(roll.get("last", "")).to_upper()
	_last.modulate.a = 0.0
	add_child(_last)
	_centre(_last, _size.y * 0.4, BIG)
	_heart = UiChrome.label(_style, "hp")
	_heart.text = "<3"
	_heart.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_heart.size = Vector2(_size.x, float(ROW_PITCH))
	_heart.position = Vector2(0.0, _size.y * 0.4 + float(ROW_PITCH * BIG) + 2.0)
	_heart.modulate.a = 0.0
	add_child(_heart)


## Puts `label` in the middle of the screen at `y`, drawn `scale` times the font. Centred by its
## MEASURED width rather than by alignment inside a box: a scaled label grows past a box it does
## not fit and stops being centred, which the first photograph of this roll showed.
func _centre(label: Label, y: float, scale: int) -> void:
	label.scale = Vector2(scale, scale)
	label.size = label.get_minimum_size()
	label.position = Vector2((_size.x - label.size.x * float(scale)) * 0.5, y)


func _physics_process(_delta: float) -> void:
	if _style == null:
		return
	_frame += 1
	if -_scroll.position.y < _scroll_end:
		_scroll.position.y -= _speed
	elif not _done:
		_done = true
	_paint()


func _paint() -> void:
	var t := float(_frame)
	for i in _stars.size():
		_stars[i].modulate.a = 0.35 + 0.65 * absf(sin(t * 0.02 + float(i) * 1.7))
	for i in _petals.size():
		var s := _petal_state[i]
		s.y += 0.35 + 0.1 * float(i % 3)
		if s.y > _size.y:
			s = Vector3(_rng.next_float(0.0, _size.x), -4.0, s.z)
		_petal_state[i] = s
		_petals[i].position = Vector2(s.x + sin(t * 0.04 + s.z) * 6.0, s.y)
		_petals[i].size = Vector2(1.0 + 2.0 * absf(cos(t * 0.05 + s.z)), 1.0)
	# Each line swells as it crosses the middle of the screen, so the eye is pulled along the roll.
	for label in _rows:
		var mid := _scroll.position.y + label.position.y + float(ROW_PITCH) * 0.5 * label.scale.y
		var near := 1.0 - clampf(absf(mid - _size.y * 0.45) / (_size.y * 0.5), 0.0, 1.0)
		label.modulate.a = clampf(near * 1.6, 0.0, 1.0)
	var walk := fmod(t * 0.5, _size.x + 80.0) - 40.0
	for i in _parade.size():
		_parade[i].position = Vector2(walk - float(i) * 22.0, _size.y - 6.0)
	if _done:
		var since := float(_frame) - _done_at()
		_last.modulate.a = clampf(since / 60.0, 0.0, 1.0)
		_heart.modulate.a = _last.modulate.a
		var beat := 1.0 + 0.25 * maxf(sin(since * 0.12), 0.0)
		_heart.scale = Vector2(beat, beat)
		_heart.pivot_offset = _heart.size * 0.5


func _done_at() -> float:
	if _done_frame < 0:
		_done_frame = _frame
	return float(_done_frame)


func _dot(size: Vector2, role: String) -> ColorRect:
	var rect := ColorRect.new()
	rect.size = size
	rect.color = _style.ui_color(role)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rect)
	return rect


func _unhandled_input(event: InputEvent) -> void:
	if _committed or not InputGate.is_press(event) or not _gate.accept(event):
		return
	if not _done:
		return
	if event.is_action_pressed(&"interact") or event.is_action_pressed(&"cancel"):
		_committed = true
		sound_wanted.emit(Sfx.id_of(Sfx.Cue.MENU_CONFIRM))
		left.emit()
		get_viewport().set_input_as_handled()


## The words on this screen are names, not prompts, so a device change has nothing to rewrite.
func reprompt(_device: Prompts.Device) -> void:
	pass
