extends Node2D

@onready var http          = $HTTPRequest
@onready var player1       = $VideoPlayer1
@onready var player2       = $VideoPlayer2
@onready var left_ctrl    = $"../../XROrigin3D/LeftController"
 

var current_player = player1
var next_player    = player2
var is_playing_chunk = false

var VIDEO_URL = "http://172.20.10.5/movies/" + GameState.voted_film + "/"
const TEMP_DIR = "user://"
const BUFFER_SIZE = 3
const CHUNK_NAME_FORMAT = "out%03d.ogv"
const CROSSFADE_DURATION = 1.0
const CHUNK_DURATION = 30.0

var buffer: Array[String] = []
var downloading = false
var playback_started = false
var playing_chunk_index = -1
var current_download_index = 0

var preload_ready = false
var preload_path = ""
var preload_stream = null

func _ready():
	http.request_completed.connect(_on_HTTPRequest_request_completed)
	left_ctrl.button_pressed.connect(_on_left_controller_button_pressed)


	current_player = player1
	next_player    = player2

	current_player.visible = true
	next_player.visible    = false

	current_player.volume = 1.0
	next_player.volume    = 0.0

	current_player.modulate.a = 1.0
	next_player.modulate.a    = 0.0

	download_next_chunk()

func play_chunk(path: String):
	print("Preparing to play: ", path)

	var stream = VideoStreamTheora.new()
	stream.set_file(path)
	await get_tree().process_frame

	next_player.stream = stream
	await get_tree().process_frame

	next_player.visible = true
	next_player.volume  = 0.0
	next_player.modulate.a = 0.0

	next_player.play()
	next_player.stream_position = 0.0

	await crossfade_players()
	swap_player()

	playback_started     = true
	is_playing_chunk     = false

func crossfade_players():
	print("Crossfading...")
	var tween = create_tween()
	tween.set_parallel(true)

	tween.tween_property(current_player, "volume", 0.0, CROSSFADE_DURATION)
	tween.tween_property(next_player,    "volume", 1.0, CROSSFADE_DURATION)

	var next_end_color    = Color(next_player.modulate.r, next_player.modulate.g, next_player.modulate.b, 1.0)
	tween.tween_property(next_player, "modulate", next_end_color, CROSSFADE_DURATION) \
		  .set_trans(Tween.TRANS_SINE) \
		  .set_ease(Tween.EASE_IN_OUT)

	await tween.finished

func _on_HTTPRequest_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray):
	downloading = false

	if result == OK and response_code == 200:
		var filename = "chunk_%03d.ogv" % current_download_index
		var path = TEMP_DIR + filename
		var file = FileAccess.open(path, FileAccess.WRITE)
		if file:
			file.store_buffer(body)
			file.close()
			buffer.append(path)
			print("Saved chunk: ", path)
			current_download_index += 1
		else:
			print("Failed to write chunk")
	else:
		print("Download failed: result=%d code=%d" % [result, response_code])

func download_next_chunk():
	var chunk_name = CHUNK_NAME_FORMAT % current_download_index
	var url = VIDEO_URL + chunk_name
	print("Downloading: ", url)
	http.request(url)
	downloading = true

func _process(_delta: float) -> void:
	while buffer.size() < BUFFER_SIZE and not downloading:
		download_next_chunk()

	if not preload_ready and buffer.size() > 0:
		preload_path   = buffer[0]
		preload_stream = VideoStreamTheora.new()
		preload_stream.set_file(preload_path)
		preload_ready  = true
		print("Preloaded:", preload_path)

	if not playback_started and preload_ready:
		buffer.pop_front()
		next_player.stream = preload_stream
		next_player.stream_position = 0.0
		next_player.visible = true
		next_player.volume  = 1.0
		next_player.modulate.a = 1.0
		next_player.play()
		swap_player()
		playback_started = true
		is_playing_chunk = false
		preload_ready     = false

	if playback_started and not is_playing_chunk:
		var time_left = CHUNK_DURATION - current_player.stream_position
		if time_left <= CROSSFADE_DURATION and preload_ready:
			is_playing_chunk = true
			buffer.pop_front()
			next_player.stream = preload_stream
			next_player.stream_position = 0.0
			next_player.visible = true
			next_player.volume  = 0.0
			next_player.modulate.a = 0.0
			next_player.play()
			await crossfade_players()
			swap_player()
			is_playing_chunk = false
			preload_ready     = false

func swap_player():
	next_player.visible    = true
	current_player.visible = false
	current_player.stop()

	current_player.modulate.a = 1.0
	next_player.modulate.a    = 1.0

	var temp = current_player
	current_player = next_player
	next_player    = temp

	print("Switched players")

# ------------- Sync-RPC -------------
@rpc("any_peer", "call_local")
func sync_play_pause(should_play: bool, pos: float) -> void:
	if not playback_started:
		return
	current_player.stream_position = pos
	current_player.set_paused(not should_play)

# ------------- VR-Trigger-Handler für linken Controller -------------
func _on_left_controller_button_pressed(name: String) -> void:
	var is_paused   = current_player.is_paused()
	var should_play = is_paused      # wenn pausiert → play, sonst pause
	var pos         = current_player.stream_position
	rpc("sync_play_pause", should_play, pos)
