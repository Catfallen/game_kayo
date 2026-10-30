extends GdUnitTestSuite
## The staff roll after a game's ending (EndingRoll): what its file may say, that it MOVES - a roll
## that stood still would be the static page it exists not to be - and that every line it draws is
## on the screen. And the air over a map (MapData.ambient, AmbientLayer), the other new surface of
## the Japan chapter: what the content gate refuses, and that petals are seeded rather than random.

const ROLL := "res://data/credits/kayo_fim.json"
const SIZE := Vector2i(320, 180)


func _style() -> SpriteStyle:
	return load("res://data/styles/lpc32.tres") as SpriteStyle


func _roll(data: Dictionary) -> EndingRoll:
	var roll: EndingRoll = auto_free(EndingRoll.new())
	add_child(roll)
	roll.setup(data, _style(), SIZE, null, 7)
	return roll


func _write(name: String, data: Variant) -> String:
	var path := "user://%s.json" % name
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
	return path


func test_the_shipped_roll_describes_itself() -> void:
	assert_array(EndingRoll.problems_of(ROLL)).is_empty()


func test_a_roll_that_is_missing_or_credits_nobody_is_refused() -> void:
	assert_str("\n".join(EndingRoll.problems_of("user://nowhere.json"))).contains("does not load")
	var empty := _write("roll_empty", {"title": "x", "blocks": []})
	assert_str("\n".join(EndingRoll.problems_of(empty))).contains("nobody would be credited")
	var nameless := _write("roll_nameless", {"blocks": [{"heading": "By", "names": []}]})
	assert_str("\n".join(EndingRoll.problems_of(nameless))).contains("names nobody")
	var typo := _write("roll_typo", {"blocks": [{"heading": "By", "names": ["A"]}], "sped": 1})
	assert_str("\n".join(EndingRoll.problems_of(typo))).contains("'sped'")
	var still := _write("roll_still", {"blocks": [{"heading": "By", "names": ["A"]}], "speed": 0})
	assert_str("\n".join(EndingRoll.problems_of(still))).contains("never move")


func test_the_roll_rises_and_then_finishes() -> void:
	var roll := _roll(EndingRoll.read(ROLL))
	assert_bool(roll.finished()).is_false()
	for i in 60:
		roll._physics_process(0.0)
	var risen := roll.scrolled()
	assert_float(risen).override_failure_message("a second in, the staff has not moved").is_greater(0.0)
	for i in 20000:
		if roll.finished():
			break
		roll._physics_process(0.0)
	assert_bool(roll.finished()).override_failure_message("the roll never reached its end").is_true()
	assert_float(roll.scrolled()).is_greater(risen)


func test_every_line_of_the_roll_is_drawn_inside_the_screen() -> void:
	# The first photograph had the big names off centre and the longest one off the right edge:
	# a scaled label grows past the box it was centred in. Every line is measured as drawn.
	var roll := _roll(EndingRoll.read(ROLL))
	var checked := 0
	for child in roll.find_children("*", "Label", true, false):
		var label := child as Label
		var left := label.position.x
		var right := left + label.size.x * label.scale.x
		assert_float(left).override_failure_message("'%s' starts off the left edge" % label.text) \
			.is_greater_equal(0.0)
		assert_float(right).override_failure_message("'%s' runs off the right edge" % label.text) \
			.is_less_equal(float(SIZE.x))
		if label.text.length() > 3:
			var middle := (left + right) * 0.5
			assert_float(absf(middle - SIZE.x * 0.5)).override_failure_message(
				"'%s' is not centred (middle at %s)" % [label.text, middle]).is_less(2.0)
		checked += 1
	assert_int(checked).is_greater(10)


func test_a_map_ambient_with_a_fault_is_refused_by_name() -> void:
	var cases := {
		"\"fog\"": {"fog": 1},
		"tint 'pink-ish' is not a colour": {"tint": "pink-ish"},
		"outside 1-": {"petals": {"count": 0, "colors": ["#ffffff"], "fall": 1}},
		"name no colours": {"petals": {"count": 4, "colors": [], "fall": 1}},
		"hang still": {"petals": {"count": 4, "colors": ["#ffffff"], "fall": 0}},
		"petals has 'size'": {"petals": {"count": 4, "colors": ["#ffffff"], "fall": 1, "size": 2}},
	}
	for said: String in cases:
		var map := MapData.from_dictionary({"id": "t", "style": "lpc32", "legend": {".": "grass"},
			"ground": ["."], "ambient": cases[said]})
		var problems := "\n".join(map.problems(["grass"]))
		assert_str(problems).override_failure_message(
			"%s was not refused for %s: %s" % [cases[said], said, problems]).contains(said.replace("\"", "'"))


func test_a_good_ambient_passes_and_survives_the_differences_check() -> void:
	var air := {"tint": "#a898cc", "petals": {"count": 12, "colors": ["#f7c3d8"], "fall": 0.7}}
	var map := MapData.from_dictionary({"id": "t", "style": "lpc32", "legend": {".": "grass"},
		"ground": ["."], "spawns": {"start": [0, 0]}, "ambient": air})
	assert_array(map.problems(["grass"])).is_empty()
	var bare := MapData.from_dictionary({"id": "t", "style": "lpc32", "legend": {".": "grass"},
		"ground": ["."]})
	assert_str(", ".join(MapData.differences(map, bare))).contains("ambient")


func test_petals_fall_the_same_way_on_every_run() -> void:
	var spec := {"count": 10, "colors": ["#f7c3d8", "#ffffff"], "fall": 0.7}
	var a: AmbientLayer = auto_free(AmbientLayer.new())
	var b: AmbientLayer = auto_free(AmbientLayer.new())
	add_child(a)
	add_child(b)
	a.setup(spec, 32, 60, 99)
	b.setup(spec, 32, 60, 99)
	assert_int(a.petal_count()).is_equal(10)
	for i in 30:
		a._physics_process(0.0)
		b._physics_process(0.0)
	assert_str(str(a._petals)).is_equal(str(b._petals))
