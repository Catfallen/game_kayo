class_name DialogScene
extends Control
## A picture that plays above the dialog box while a line is on screen - the event scene of the
## genre, where a hug or a goodbye is SHOWN rather than described: Pokemon's cutscene stills,
## Mother 3's close-ups, a visual novel's CG. A dialog node names one with `scene`.
##
## The art is a strip: equal frames side by side in one PNG, with a `<name>.json` beside it -
##   {"frames": 12, "hold": 8, "loop_from": 4}
## `hold` is how many physics frames each picture stays up (one number, or one per picture), and
## after the last picture the strip goes back to `loop_from`, so a hug can close in once and then
## hold on its squeeze for as long as the words take. Counted in PHYSICS frames rather than
## seconds, the rule every animation here follows, so a scripted session sees the same picture on
## the same frame on any machine.
##
## Drawn at the design scale - one art pixel is one interface pixel - which is twice the size of
## the world in a 32px style: a close-up, the way the genre frames these moments.
##
## A Control that draws its own picture rather than a TextureRect: the layout audits find a
## portrait as the TextureRect in the box, and a scene is not anybody's face.

var path := ""
var _sheet: Texture2D = null
var _cell := Vector2.ZERO
var _frames := 1
var _holds: Array[int] = []
var _loop_from := 0
var _index := 0
var _tick := 0


static func meta_path(png: String) -> String:
	return png.get_basename() + ".json"


## Everything wrong with a scene a dialog names, for the content gate - a missing picture is a
## goodbye the player never sees, and every headless gate would pass it.
static func problems_of(png: String) -> Array[String]:
	var out: Array[String] = []
	if not ResourceLoader.exists(png):
		out.append("scene '%s' does not exist" % png)
		return out
	var meta := JsonFile.read(meta_path(png))
	if not meta.ok:
		out.append("scene '%s' has no readable %s: %s" % [png, meta_path(png), meta.error])
		return out
	var frames := int(meta.data.get("frames", 0))
	if frames < 1:
		out.append("scene '%s' has %d frames" % [png, frames])
		return out
	var texture := load(png) as Texture2D
	if texture != null and texture.get_width() % frames != 0:
		out.append("scene '%s' is %d wide, which is not %d equal frames" % [png, texture.get_width(), frames])
	var loop_from := int(meta.data.get("loop_from", 0))
	if loop_from < 0 or loop_from >= frames:
		out.append("scene '%s' loops back to frame %d of %d" % [png, loop_from, frames])
	var hold: Variant = meta.data.get("hold", 1)
	if hold is Array and (hold as Array).size() != frames:
		out.append("scene '%s' holds %d pictures and has %d" % [png, (hold as Array).size(), frames])
	return out


func _init() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	mouse_filter = Control.MOUSE_FILTER_IGNORE


## Starts a strip from its first picture. The same strip asked for again keeps playing, so a hug
## that spans three lines of a conversation is one hug and not three.
func play(png: String) -> bool:
	if png == path:
		return true
	var sheet := load(png) as Texture2D
	var meta := JsonFile.read(meta_path(png))
	if sheet == null or not meta.ok:
		push_error("DialogScene: scene '%s' cannot be shown" % png)
		return false
	path = png
	_frames = maxi(1, int(meta.data.get("frames", 1)))
	_loop_from = clampi(int(meta.data.get("loop_from", 0)), 0, _frames - 1)
	_holds.clear()
	var hold: Variant = meta.data.get("hold", 1)
	for i in _frames:
		_holds.append(maxi(1, int((hold as Array)[i]) if hold is Array else int(hold)))
	_sheet = sheet
	_cell = Vector2(sheet.get_width() / _frames, sheet.get_height())
	size = _cell
	_show(0)
	return true


func stop() -> void:
	path = ""


func picture() -> int:
	return _index


## One physics frame.
func step() -> void:
	if path.is_empty():
		return
	_tick += 1
	if _tick < _holds[_index]:
		return
	_show(_index + 1 if _index + 1 < _frames else _loop_from)


func _show(index: int) -> void:
	_index = index
	_tick = 0
	queue_redraw()


func _draw() -> void:
	if _sheet != null and not path.is_empty():
		draw_texture_rect_region(_sheet, Rect2(Vector2.ZERO, _cell),
			Rect2(Vector2(_cell.x * _index, 0.0), _cell))
