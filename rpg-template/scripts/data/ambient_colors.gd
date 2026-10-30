class_name AmbientColors
extends RefCounted
## The colours a map's `ambient` names, read from their hex strings. Here in scripts/data because a
## map's air is coloured by DATA, and the linter keeps every `Color` out of scripts/world - the one
## place a hex string becomes a colour is the data layer, the way a SpriteStyle's ramps are.


static func valid(text: Variant) -> bool:
	return Color.html_is_valid(str(text))


## The colour `text` spells, or white when it spells none - `MapData.problems` has refused that map
## already, so this is never the colour anybody sees.
static func of(text: Variant) -> Color:
	return Color.html(str(text)) if valid(text) else Color.WHITE
