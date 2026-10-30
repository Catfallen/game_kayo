class_name BattleFx
extends Node2D
## What a turn fight LOOKS like when something happens: a blow shakes and flashes what it hit and
## throws its number up off it, a timed hit rocks the whole field, a spell plays the shape of its
## kind, and a fallen fighter fades.
##
## A VIEW of the fight and nothing else. It is told about events by BattleScreen, which reads them
## off BattleLogic's own numbers - health going down or up, a cast counted - so the rules hold no
## drawing and a fight plays identically with this layer gone. Counted in PHYSICS FRAMES, never
## seconds or tweens, the battle screen's own rule, so a replayed fight draws the same.
##
## Every colour is a ROLE off the style, because a colour literal in scripts/ui/ fails the build.

const NUMBER_FRAMES := 40
const NUMBER_RISE := 14.0
const FLASH_FRAMES := 12
const SHAKE_FRAMES := 14
const ICON_FRAMES := 54
const SWEEP_FRAMES := 18
const DROP_FRAMES := 30
const SPARK_FRAMES := 16
const FADE_FRAMES := 24
const DOWN_ALPHA := 0.35
## A throw: the ball's flight, three wobbles on the ground, and how long it lingers after a catch.
## Sized against the fight's own message pace (45 frames a line, three lines), so the result
## lands as its line does.
const THROW_FLY := 22
const THROW_WOBBLE := 22
const THROW_LINGER := 40
const THROW_ARC := 30.0

var _style: SpriteStyle = null
## Short-lived pieces: {node, age, life, kind, from, to}.
var _pieces: Array[Dictionary] = []
## Per-view reactions, keyed by the view's instance id: {flash, shake, power, fade}.
var _reactions: Dictionary = {}
var _quake_left := 0
## The one throw in flight: {node, age, from, to, view, caught, blocked}. Empty when none is.
var _throw: Dictionary = {}
var _quake_power := 0.0


func setup(style: SpriteStyle) -> void:
	_style = style


## One frame of every running effect. Called once per physics frame by the screen.
func tick() -> void:
	if _quake_left > 0:
		_quake_left -= 1
	for key: Variant in _reactions.keys():
		var r: Dictionary = _reactions[key]
		r["flash"] = maxi(int(r["flash"]) - 1, 0)
		r["shake"] = maxi(int(r["shake"]) - 1, 0)
		if int(r["fade"]) > 0:
			r["fade"] = int(r["fade"]) - 1
		if int(r.get("hide", 0)) > 0:
			r["hide"] = int(r["hide"]) - 1
		if int(r.get("hide_in", 0)) > 0:
			r["hide_in"] = int(r["hide_in"]) - 1
	_tick_throw()
	var alive: Array[Dictionary] = []
	for piece in _pieces:
		piece["age"] = int(piece["age"]) + 1
		var node: CanvasItem = piece["node"]
		# A piece may wait its turn before it shows: a wind-up is a sequence, not one burst.
		var waited := int(piece["age"]) - int(piece.get("wait", 0))
		node.visible = waited > 0
		if waited <= 0:
			alive.append(piece)
			continue
		if waited == 1 and piece.has("quake"):
			quake(float(piece["quake"]))
		var t := float(waited) / float(piece["life"])
		if t >= 1.0:
			node.queue_free()
			continue
		var from: Vector2 = piece["from"]
		var to: Vector2 = piece["to"]
		node.position = from.lerp(to, _ease(t, StringName(piece["kind"])))
		# The last third fades out, so nothing pops off the screen.
		node.modulate.a = clampf((1.0 - t) * 3.0, 0.0, 1.0)
		if StringName(piece["kind"]) == &"flash":
			node.modulate.a = 0.85 * sin(PI * t)
		if StringName(piece["kind"]) == &"icon":
			var pop := 1.0 + 0.6 * maxf(0.0, 1.0 - t * 5.0)
			node.scale = Vector2(pop, pop) * float(piece.get("base_scale", 1.0))
		alive.append(piece)
	_pieces = alive


## The offset the whole field is drawn at this frame: the quake, decaying.
func field_offset() -> Vector2:
	if _quake_left <= 0:
		return Vector2.ZERO
	var side := 1.0 if (_quake_left / 2) % 2 == 0 else -1.0
	var size := _quake_power * float(_quake_left) / float(SHAKE_FRAMES)
	return Vector2(side * size, (side * -0.5) * size)


## Where `view` is drawn this frame, on top of where the screen put it.
func offset_for(view: Node) -> Vector2:
	var r: Dictionary = _reactions.get(view.get_instance_id(), {})
	if r.is_empty() or int(r["shake"]) <= 0:
		return field_offset()
	var side := 1.0 if (int(r["shake"]) / 2) % 2 == 0 else -1.0
	return field_offset() + Vector2(side * float(r["power"]), 0.0)


## Tints `view` for this frame: lit on alternate frames while flashing, faded once it has fallen,
## plain otherwise. `lightened(1.0)` is white at the view's own alpha, which is how a plain tint is
## reached with no colour literal.
func dress(view: CanvasItem, down: bool) -> void:
	var r: Dictionary = _reactions.get(view.get_instance_id(), {})
	var plain := view.modulate.lightened(1.0)
	# Inside a ball: -1 is for good, a positive count is until it breaks free.
	var hidden := int(r.get("hide", 0)) if not r.is_empty() else 0
	if hidden != 0 and int(r.get("hide_in", 0)) <= 0:
		plain.a = 0.0
		view.modulate = plain
		return
	if not r.is_empty() and int(r["flash"]) > 0 and (int(r["flash"]) / 2) % 2 == 0:
		view.modulate = _bright(_style.ui_color("hp"))
		return
	plain.a = 1.0
	if down:
		var fade_left := int(r.get("fade", 0)) if not r.is_empty() else 0
		plain.a = lerpf(DOWN_ALPHA, 1.0, float(fade_left) / float(FADE_FRAMES))
	view.modulate = plain


# -- what can happen --------------------------------------------------------------------------


## `view` took a blow worth `amount`, its feet at `feet`, `tall` pixels high.
func hurt(view: Node2D, feet: Vector2, tall: float, amount: int, heavy: bool) -> void:
	var r := _reaction(view)
	r["flash"] = FLASH_FRAMES
	r["shake"] = SHAKE_FRAMES
	r["power"] = 3.0 if heavy else 2.0
	_number(feet - Vector2(0.0, tall), "-%d" % amount, "hp")
	_impact(feet - Vector2(0.0, tall * 0.55), heavy)


## `view` was healed by `amount`.
func healed(view: Node2D, feet: Vector2, tall: float, amount: int) -> void:
	_number(feet - Vector2(0.0, tall), "+%d" % amount, "mp")
	_drops(feet - Vector2(0.0, tall + 10.0), tall, "mp")


## `view` has just fallen: it fades rather than vanishing, because a foe that vanished mid-fight
## would read as having fled.
func fell(view: Node2D) -> void:
	_reaction(view)["fade"] = FADE_FRAMES


## The whole field rocks, for a hit timed to the beat.
func quake(power: float) -> void:
	_quake_left = SHAKE_FRAMES
	_quake_power = power


## A spell was cast. `caster_head` is above the caster; `targets` are the feet of what it reached.
func cast(row: BattleLogic.SpellRow, caster_head: Vector2, targets: Array[Vector2], tall: float) -> void:
	if row.icon != null:
		_icon(row.icon, caster_head)
	match row.kind:
		SpellDef.Kind.HEAL:
			pass  # the heal's own number and drops come from `healed`
		SpellDef.Kind.BOOST:
			_sparks(caster_head + Vector2(0.0, tall * 0.5), tall, "hp")
			_number(caster_head - Vector2(0.0, 6.0), tr("ATK+") if row.stat == SpellDef.Stat.ATTACK
				else tr("DEF+"), "hp")
		SpellDef.Kind.SAP, SpellDef.Kind.SLEEP:
			for at in targets:
				_sparks(at - Vector2(0.0, tall * 0.4), tall, "mp")
		_ when row.target == SpellDef.Target.ALL:
			if not targets.is_empty():
				var left := targets[0].x
				var right := targets[0].x
				for at in targets:
					left = minf(left, at.x)
					right = maxf(right, at.x)
				_sweep(left - 24.0, right + 24.0, targets[0].y - tall * 0.5)
			quake(2.0)
		_:
			quake(3.0)


## A capture item thrown from `from` at the foe drawn by `view`, standing at `to`. `caught` and
## `blocked` are already decided - the rules settled them on the press - so the animation only has
## to arrive at the answer on the beat its line is shown.
func capture(view: Node2D, from: Vector2, to: Vector2, icon: Texture2D, caught: bool, blocked: bool) -> void:
	if not _throw.is_empty():
		(_throw["node"] as Node).queue_free()
	var ball: Node2D
	if icon != null:
		var sprite := Sprite2D.new()
		sprite.texture = icon
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		var fit := 10.0 / maxf(float(icon.get_width()), 1.0)
		sprite.scale = Vector2(fit, fit)
		ball = sprite
	else:
		ball = Node2D.new()
		var dot := _rect(Vector2(6.0, 6.0), "text")
		dot.position = Vector2(-3.0, -3.0)
		ball.add_child(dot)
	add_child(ball)
	ball.position = from
	_throw = {"node": ball, "age": 0, "from": from, "to": to, "view": view, "caught": caught,
		"blocked": blocked}
	if not blocked:
		var r := _reaction(view)
		r["hide_in"] = THROW_FLY
		r["hide"] = -1 if caught else THROW_FLY + THROW_WOBBLE * 3


func _tick_throw() -> void:
	if _throw.is_empty():
		return
	var ball: Node2D = _throw["node"]
	var age := int(_throw["age"]) + 1
	_throw["age"] = age
	var from: Vector2 = _throw["from"]
	var to: Vector2 = _throw["to"]
	var wobble_end := THROW_FLY + THROW_WOBBLE * 3
	if age <= THROW_FLY:
		var t := float(age) / float(THROW_FLY)
		ball.position = from.lerp(to, t) - Vector2(0.0, THROW_ARC * sin(PI * t))
		ball.rotation += 0.5
		if age == THROW_FLY and not bool(_throw["blocked"]):
			_burst(to, "text")
		return
	if bool(_throw["blocked"]):
		# Batted away: it flies back up and off, and fades.
		var t := float(age - THROW_FLY) / 24.0
		ball.position = to + Vector2(-40.0 * t, -30.0 * sin(PI * minf(t, 1.0) * 0.5))
		ball.modulate.a = clampf(1.0 - t, 0.0, 1.0)
		if t >= 1.0:
			_end_throw()
		return
	if age <= wobble_end:
		ball.position = to
		var into := (age - THROW_FLY) % THROW_WOBBLE
		ball.rotation = 0.45 * sin(TAU * float(into) / 12.0) if into < 12 else 0.0
		if age == wobble_end:
			if bool(_throw["caught"]):
				_sparks(to, 26.0, "select")
				_sparks(to + Vector2(0.0, -4.0), 20.0, "text")
			else:
				_burst(to, "hp")
				_end_throw()
		return
	var linger := float(age - wobble_end) / float(THROW_LINGER)
	ball.modulate.a = clampf(1.0 - linger, 0.0, 1.0)
	if linger >= 1.0:
		_end_throw()


func _end_throw() -> void:
	(_throw["node"] as Node).queue_free()
	_throw = {}


## A ring of light thrown out from a point: a foe going into a ball, or breaking out of one.
func _burst(at: Vector2, role: String) -> void:
	for i in 12:
		var angle := TAU * float(i) / 12.0
		var bit := _rect(Vector2(2.0, 2.0), role)
		_add(bit, SPARK_FRAMES, &"spark", at, at + Vector2(cos(angle), sin(angle)) * 16.0)


## A foe's move winding up across its cue, `frames` long, so whatever it draws lands on the impact.
## `kind` is one of `EnemyDef.MOVE_FX`; `from` is the foe's feet, `to` its target's, `screen` the
## size of the field for the shapes that fill it. An empty or unknown kind draws nothing - the
## lean every foe already has is the wind-up then.
func foe_move(kind: String, from: Vector2, to: Vector2, tall: float, frames: int,
		screen: Vector2) -> void:
	var span := maxi(frames, 8)
	var head := from - Vector2(0.0, tall * 0.6)
	var chest := to - Vector2(0.0, tall * 0.5)
	match kind:
		"shards":
			# Crystal spikes break through the floor in a line from the foe to its target.
			for i in 7:
				var at := from.lerp(to, float(i + 1) / 7.0) + Vector2(0.0, 2.0)
				var wait := span / 3 + i * (span / 3) / 7
				var spike := _rect(Vector2(3.0, 8.0 + i), "text" if i % 2 == 0 else "border")
				_add(spike, maxi(span - wait, 6), &"spark", at, at - Vector2(0.0, 14.0 + i * 1.5),
					{"wait": wait})
			for i in 5:
				var bit := _rect(Vector2(2.0, 7.0), "text")
				var at := to + Vector2((float(i) - 2.0) * 5.0, 2.0)
				_add(bit, 14, &"spark", at, at - Vector2(0.0, tall * 0.8), {"wait": span - 6})
		"beam":
			# Light gathers on the foe, then a prism of colours crosses to the target.
			for i in 10:
				var angle := TAU * float(i) / 10.0
				var bit := _rect(Vector2(3.0, 3.0), "text" if i % 2 == 0 else "border")
				_add(bit, span * 2 / 3, &"sweep", head + Vector2(cos(angle), sin(angle)) * 26.0,
					head)
			var roles := ["hp", "text", "dim", "border"]
			for i in 12:
				var bolt := _rect(Vector2(12.0, 3.0), roles[i % roles.size()])
				var lane := Vector2(0.0, float(i % 3 - 1) * 2.0)
				_add(bolt, 10, &"sweep", head + lane, chest + lane, {"wait": span * 2 / 3 + i})
		"rush":
			# The foe itself crosses the field (the screen moves it); dust is thrown off its path.
			for i in 6:
				var at := from.lerp(to, float(i) / 6.0) + Vector2(0.0, -2.0)
				var dust := _rect(Vector2(3.0, 3.0), "text" if i % 2 == 0 else "dim")
				_add(dust, 16, &"spark", at, at + Vector2(6.0, -6.0 - i), {"wait": span / 2 + i * span / 14})
		"quake":
			# The floor trembles, more and more, and cracks run out under the party.
			for k in 3:
				var crack := _rect(Vector2(3.0, 2.0), "text")
				var start := from + Vector2(0.0, 3.0 + k * 2.0)
				_add(crack, span / 2, &"sweep", start, to + Vector2(-20.0 + k * 20.0, 3.0 + k * 2.0),
					{"wait": span / 2})
			for i in 3:
				_add(Node2D.new(), 1, &"spark", from, from, {"wait": span / 4 * (i + 1), "quake": 1.5 + i})
		"storm":
			# Crystals fall out of the dark above onto the target, one after another.
			for i in 9:
				var x := (float(i % 5) - 2.0) * 7.0
				var start := Vector2(to.x + x, -8.0)
				var shard := _rect(Vector2(4.0, 8.0), "text" if i % 2 == 0 else "border")
				var wait := span / 3 + i * (span * 2 / 3 - 10) / 9
				_add(shard, 14, &"drop", start, Vector2(to.x + x, chest.y + 6.0), {"wait": wait})
		"flash":
			# Facets glint on the foe, then the whole field goes white for a moment.
			_sparks(head, tall, "text")
			var glare := _rect(screen, "text")
			glare.modulate.a = 0.0
			_add(glare, 24, &"flash", Vector2.ZERO, Vector2.ZERO, {"wait": span - 12})


# -- the pieces -------------------------------------------------------------------------------


func _reaction(view: Node) -> Dictionary:
	var key := view.get_instance_id()
	if not _reactions.has(key):
		_reactions[key] = {"flash": 0, "shake": 0, "power": 0.0, "fade": 0, "hide": 0, "hide_in": 0}
	return _reactions[key]


func _bright(c: Color) -> Color:
	var out := c * 2.2
	out.a = 1.0
	return out


func _ease(t: float, kind: StringName) -> float:
	if kind == &"drop":
		return t * t
	if kind == &"sweep":
		return t
	return 1.0 - (1.0 - t) * (1.0 - t)


func _add(node: CanvasItem, life: int, kind: StringName, from: Vector2, to: Vector2,
		extra: Dictionary = {}) -> void:
	add_child(node)
	node.position = from
	var piece := {"node": node, "age": 0, "life": life, "kind": kind, "from": from, "to": to}
	piece.merge(extra)
	_pieces.append(piece)


func _number(at: Vector2, text: String, role: String) -> void:
	var label := UiChrome.label(_style, role)
	label.text = text
	label.add_theme_color_override("font_outline_color", _style.ui_color("panel"))
	label.add_theme_constant_override("outline_size", 2)
	var width := label.get_minimum_size().x
	var from := at - Vector2(width * 0.5, 10.0)
	_add(label, NUMBER_FRAMES, &"number", from, from - Vector2(0.0, NUMBER_RISE))


func _rect(size: Vector2, role: String) -> ColorRect:
	var rect := ColorRect.new()
	rect.size = size
	rect.color = _style.ui_color(role)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return rect


## A star of four short strokes thrown out from the point of contact.
func _impact(at: Vector2, heavy: bool) -> void:
	var reach := 12.0 if heavy else 8.0
	for i in 8:
		var angle := TAU * float(i) / 8.0
		var dir := Vector2(cos(angle), sin(angle))
		var bit := _rect(Vector2(2.0, 2.0), "text" if i % 2 == 0 else "hp")
		_add(bit, SPARK_FRAMES, &"spark", at, at + dir * reach)


## Water falling onto a fighter: drops in a row, staggered by starting height so they land in turn.
func _drops(top: Vector2, tall: float, role: String) -> void:
	for i in 6:
		var x := (float(i) - 2.5) * 5.0
		var start := top + Vector2(x, -float(i % 3) * 6.0)
		var bit := _rect(Vector2(2.0, 3.0), role)
		_add(bit, DROP_FRAMES, &"drop", start, start + Vector2(0.0, tall))


## Sparks rising off a fighter, for a lift or a charm.
func _sparks(base: Vector2, tall: float, role: String) -> void:
	for i in 7:
		var x := (float(i) - 3.0) * 4.0
		var start := base + Vector2(x, float(i % 2) * 4.0)
		var bit := _rect(Vector2(2.0, 2.0), role)
		_add(bit, SPARK_FRAMES + 10, &"spark", start, start - Vector2(0.0, tall * 0.9))


## A lash drawn across everything at once: a bright stroke that cracks from one side to the other.
func _sweep(left: float, right: float, y: float) -> void:
	var lash := _rect(Vector2(26.0, 2.0), "text")
	_add(lash, SWEEP_FRAMES, &"sweep", Vector2(left, y), Vector2(right, y - 4.0))
	var tail := _rect(Vector2(14.0, 2.0), "hp")
	_add(tail, SWEEP_FRAMES, &"sweep", Vector2(left - 12.0, y + 2.0), Vector2(right - 12.0, y - 2.0))


func _icon(texture: Texture2D, at: Vector2) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = texture
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var fit := 16.0 / maxf(float(texture.get_width()), 1.0)
	_add(sprite, ICON_FRAMES, &"icon", at, at - Vector2(0.0, 10.0), {"base_scale": fit})
