extends GdUnitTestSuite
## The picture a dialog line can play above the box (DialogScene): what the content gate refuses,
## and how the strip is stepped - counted in physics frames, looping back where its file says.

## A shipped strip, so the clock is checked against real art and its real file.
const STRIP := "res://assets/kayo/cenas/abraco.png"


func test_a_dialog_naming_a_missing_scene_is_refused() -> void:
	var runner := DialogRunner.from_dict({"id": "s", "start": "a", "nodes": {
		"a": {"speaker": "A", "text": "look", "scene": "res://assets/nowhere/hug.png"}}})
	var said := "\n".join(runner.problems())
	assert_str(said).contains("node 'a' shows a scene")
	assert_str(said).contains("does not exist")


func test_a_dialog_naming_a_real_scene_passes_and_reaches_the_line() -> void:
	var runner := DialogRunner.from_dict({"id": "s", "start": "a", "nodes": {
		"a": {"speaker": "A", "text": "look", "scene": STRIP}}})
	assert_array(runner.problems()).is_empty()
	assert_bool(runner.begin()).is_true()
	assert_str(runner.line().scene).is_equal(STRIP)


func test_a_line_with_no_scene_names_none() -> void:
	var runner := DialogRunner.from_dict({"id": "s", "start": "a", "nodes": {
		"a": {"speaker": "A", "text": "plain"}}})
	assert_bool(runner.begin()).is_true()
	assert_str(runner.line().scene).is_empty()


func test_every_shipped_scene_describes_itself() -> void:
	var dir := "res://assets/kayo/cenas/"
	var count := 0
	for name in DirAccess.get_files_at(dir):
		if name.get_extension() != "png":
			continue
		count += 1
		assert_array(DialogScene.problems_of(dir + name)).override_failure_message(name).is_empty()
	assert_int(count).is_greater(0)


func test_the_strip_is_shown_one_picture_at_a_time_and_loops_where_it_says() -> void:
	var meta := JsonFile.read(DialogScene.meta_path(STRIP))
	var frames := int(meta.data["frames"])
	var holds: Array = meta.data["hold"]
	var loop_from := int(meta.data["loop_from"])
	var scene: DialogScene = auto_free(DialogScene.new())
	assert_bool(scene.play(STRIP)).is_true()
	# One picture, not the whole strip.
	var sheet := load(STRIP) as Texture2D
	assert_vector(scene.size).is_equal(Vector2(sheet.get_width() / frames, sheet.get_height()))
	assert_int(scene.picture()).is_equal(0)
	for i in int(holds[0]) - 1:
		scene.step()
	assert_int(scene.picture()).is_equal(0)
	scene.step()
	assert_int(scene.picture()).is_equal(1)
	# To the end, and back to where the file says the loop starts.
	for k in range(1, frames):
		for i in int(holds[k]):
			scene.step()
	assert_int(scene.picture()).is_equal(loop_from)


func test_asking_for_the_strip_already_playing_does_not_restart_it() -> void:
	var scene: DialogScene = auto_free(DialogScene.new())
	scene.play(STRIP)
	for i in 200:
		scene.step()
	var at := scene.picture()
	scene.play(STRIP)
	assert_int(scene.picture()).is_equal(at)
