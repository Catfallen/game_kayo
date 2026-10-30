class_name I18n
extends RefCounted
## A game's language, as data: `data/i18n/<id>.json` holds `locale` and `messages`, the template's
## own English sentence -> the game's. Built into a Translation at runtime rather than imported from
## CSV, so the file diffs as text and needs no import step.
##
## A sentence with a `%s` in it is translated BEFORE it is formatted, so the key is the template's
## format string exactly as the code writes it. A sentence the file does not name stays English,
## which is the honest failure: a missing line reads as untranslated, never as blank.

const ROOT := "res://data/i18n"


static func path_of(language: StringName) -> String:
	return "%s/%s.json" % [ROOT, language]


static func exists(language: StringName) -> bool:
	return FileAccess.file_exists(path_of(language))


## The Translation for `language`, or null when there is no such file or it is not a language file.
static func load_translation(language: StringName) -> Translation:
	if not exists(language):
		return null
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path_of(language)))
	if not parsed is Dictionary:
		return null
	var data: Dictionary = parsed
	var messages: Variant = data.get("messages", null)
	if not messages is Dictionary:
		return null
	var out := Translation.new()
	out.locale = str(data.get("locale", language))
	var table: Dictionary = messages
	for key: Variant in table.keys():
		out.add_message(StringName(str(key)), StringName(str(table[key])))
	return out
