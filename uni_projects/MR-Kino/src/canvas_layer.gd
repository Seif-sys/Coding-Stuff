# === CanvasLayer.gd ===
extends CanvasLayer

var is_ready = false
var update_timer := 0.0
var button = Button.new()

func _ready():
	show_menu("ControlMain")
	_fetch_movies_from_server()
	$HTTPRequestMovies.request_completed.connect(_on_movies_request_completed)

	# === Signalverbindungen ===
	$ControlMain/ButtonFilm.pressed.connect(_on_ButtonFilm_pressed)
	$ControlMain/ButtonQuit.pressed.connect(_on_ButtonQuit_pressed)
	$ControlFilmwahl/FilmButtonContainer.add_child(button)
	$ControlFilmwahl/ButtonReturnToMain.pressed.connect(_on_ButtonReturnToMain_pressed)
	$ControlSzene/ButtonMixedReality.pressed.connect(_on_ButtonMixedReality_pressed)
	$ControlSzene/ButtonKinoVR.pressed.connect(_on_ButtonKinoVR_pressed)
	$ControlSzene/ButtonWohnzimmerVR.pressed.connect(_on_ButtonWohnzimmerVR_pressed)
	$ControlSzene/ButtonReturnToFilmwahl.pressed.connect(_on_ButtonReturnToFilmwahl_pressed)
	$ControlStart/ButtonStartLobby.pressed.connect(_on_ButtonStartLobby_pressed)
	$ControlStart/ButtonReturnToSzene.pressed.connect(_on_ButtonReturnToSzene_pressed)
	$ControlLobby/ButtonReady.pressed.connect(_on_ButtonReady_pressed)
	$ControlLobby/ButtonReturnToStart.pressed.connect(_on_ButtonReturnToStart_pressed)
	$ControlLobby/ButtonWeiter.pressed.connect(_on_ButtonWeiter_pressed)
	$ControlFinalStart/ButtonReturnToLobby.pressed.connect(_on_ButtonReturnToLobby_pressed)
	$ControlFinalStart/ButtonStartFilm.pressed.connect(_on_ButtonStartFilm_pressed)

func _fetch_movies_from_server():
	var url = "http://172.20.10.5/movies/"
	$HTTPRequestMovies.request(url)

func _on_movies_request_completed(result, response_code, headers, body):
	if response_code != 200:
		print("Fehler beim Abrufen der Filme!")
		return

	var html = body.get_string_from_utf8()
	var film_names = []
	var regex = RegEx.new()
	regex.compile(r"<a href=\"([^/]+)/\">")

	for match in regex.search_all(html):
		var folder = match.get_string(1)
		film_names.append(folder)

	GameState.available_films = film_names
	_create_film_buttons()

func _on_ButtonFilm_pressed():
	_create_film_buttons()
	show_menu("ControlFilmwahl")

func _create_film_buttons():
	var film_names = GameState.available_films
	var container = $ControlFilmwahl/FilmButtonContainer
	for child in container.get_children():
		child.queue_free()

	for i in range(film_names.size()):
		var film_name = film_names[i]
		var button = Button.new()
		button.text = film_name
		button.name = "FilmButton_%d" % i
		button.pressed.connect(_on_film_button_pressed.bind(i))
		container.add_child(button)
	set_process(true)

func _process(delta):
	if $ControlLobby.visible:
		update_timer += delta
		if update_timer >= 1.0:
			update_timer = 0
			update_lobby_ui()

func show_menu(menu_name: String):
	for child in get_children():
		if child is Control:
			child.visible = false
	get_node(menu_name).visible = true

func _on_ButtonQuit_pressed():
	get_tree().quit()

func _on_ButtonReturnToMain_pressed():
	show_menu("ControlMain")

# === Szenenauswahl ===
func _on_ButtonMixedReality_pressed():
	_save_user_data("MixedReality")
	Network.start_lobby()
	show_menu("ControlStart")

func _on_ButtonKinoVR_pressed():
	_save_user_data("KinoVR")
	Network.start_lobby()
	show_menu("ControlStart")

func _on_ButtonWohnzimmerVR_pressed():
	_save_user_data("WohnzimmerVR")
	Network.start_lobby()
	show_menu("ControlStart")

func _on_ButtonReturnToFilmwahl_pressed():
	show_menu("ControlFilmwahl")

func _save_user_data(scene_name: String):
	GameState.player_name = $ControlMain/LineEdit.text
	GameState.selected_scene = scene_name
	_update_control_start()

func _update_control_start():
	$ControlStart/LabelName.text = "Name: " + GameState.player_name
	$ControlStart/LabelFilm.text = "Film: " + GameState.selected_film
	$ControlStart/LabelSzene.text = "Szene: " + GameState.selected_scene

func _on_ButtonStartLobby_pressed():
	show_menu("ControlLobby")

func _on_ButtonReturnToSzene_pressed():
	show_menu("ControlSzene")

# === Lobby-Status ===
func _on_ButtonReady_pressed():
	is_ready = true
	$ControlLobby/LabelReadyStatus.text = "✅ Du bist bereit. Warte auf andere Spieler..."

	if Network.is_host:
		for player in GameState.player_list:
			if player.name == GameState.player_name:
				player.ready = true
		Network._sync_lobby_with_all()
	else:
		Network.rpc_id(1, "set_ready_status", GameState.player_name, true)

func update_lobby_ui():
	_update_lobby_name_list()
	if _check_all_ready():
		$ControlLobby/LabelReadyStatus.text = "🎬 Alle Spieler sind bereit!"
		$ControlLobby/ButtonWeiter.disabled = false
	else:
		$ControlLobby/ButtonWeiter.disabled = true

func _update_lobby_name_list():
	var list = ""
	for player in GameState.player_list:
		list += player.name + (" ✅" if player.ready else " ❌") + "\n"
	$ControlLobby/LabelNameList.text = list

func _check_all_ready() -> bool:
	for player in GameState.player_list:
		if not player.ready:
			return false
	return true

func _on_ButtonReturnToStart_pressed():
	show_menu("ControlStart")

func _on_ButtonWeiter_pressed():
	if _check_all_ready():
		_update_final_start()
		
		if Network.is_host:
			Network.evaluate_vote_results()
		show_menu("ControlFinalStart")
		_update_final_start()
		


# === Filmwahl ===
func _on_film_button_pressed(index: int):
	GameState.selected_film = GameState.available_films[index]
	print("🎬 Film gewählt: ", GameState.selected_film)
	show_menu("ControlSzene")

# === Ergebnisanzeige ===
func _on_ButtonReturnToLobby_pressed():
	show_menu("ControlLobby")

func _update_final_start():
	var film = GameState.voted_film
	var scene = GameState.voted_scene
	$ControlFinalStart/LabelFilmSzene.text = "Film: %s | Szene: %s" % [film, scene]



@rpc("authority")
func receive_vote_result(film, scene):
	print("📥 receive_vote_result() wurde aufgerufen")
	GameState.voted_film = film
	GameState.voted_scene = scene
	show_menu("ControlFinalStart")  # Zeigt das Ergebnis-Menü an
	update_final_result()          # Füllt das Label



func update_final_result():
	var film = GameState.voted_film
	var scene = GameState.voted_scene
	print("🖥️ Ergebnis anzeigen:", film, "/", scene)
	if $ControlFinalStart/LabelFilmSzene:
		$ControlFinalStart/LabelFilmSzene.text = "Film: %s | Szene: %s" % [film, scene]
	else:
		print("❌ LabelFilmSzene wurde nicht gefunden!")

func _on_ButtonStartFilm_pressed():
	if Network.is_host:
		print("🎬 Host drückt Start – Szene:", GameState.voted_scene)
		Network.rpc("start_film_for_all", GameState.voted_scene)
		Network.start_film_for_all(GameState.voted_scene)
