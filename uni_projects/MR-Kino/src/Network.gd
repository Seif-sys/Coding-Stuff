# === Network.gd ===
extends Node

# === Variablen für Netzwerksteuerung ===
var is_host := false                      # Bin ich der Host?
var udp := PacketPeerUDP.new()           # UDP für Broadcast
var udp_port := 9999                     # UDP-Port
var host_ip := ""                         # IP des Hosts
var lobby_started := false               # Wird gerade gesucht?
var search_start_time := 0               # Startzeit der IP-Suche
var retry_timer := 0.0                   # Timer für Broadcast-Wiederholung
var own_ip := ""                          # Eigene IP-Adresse
var found_ips := []                      # Gefundene IPs im LAN
var sync_timer := 0.0                    # Timer für Namenslisten-Sync
var peer_to_name := {}                   # Verknüpft Peer-ID mit Spielernamen

func _ready():
	udp.set_broadcast_enabled(true)
	udp.set_dest_address("255.255.255.255", udp_port)
	udp.bind(udp_port, "*")
	set_process(true)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)

# === Lobby-Suche starten ===
func start_lobby():
	print("📡 Suche sofort nach vorhandenem Host...")
	var temp_udp := PacketPeerUDP.new()
	temp_udp.set_broadcast_enabled(true)
	temp_udp.set_dest_address("255.255.255.255", udp_port)
	temp_udp.bind(udp_port + 1, "*")
	temp_udp.put_packet("ARE_YOU_HOST".to_utf8_buffer())

	# Warte bis 3 Sekunden auf Antwort
	var timer := 0.0
	while timer < 3.0:
		timer += 0.1
		await get_tree().create_timer(0.1).timeout
		if temp_udp.get_available_packet_count() > 0:
			var response = temp_udp.get_packet().get_string_from_utf8()
			var ip = temp_udp.get_packet_ip()
			if response == "I_AM_HOST":
				print("✅ Host erkannt:", ip)
				_connect_as_client(ip)
				return

	# Kein Host gefunden, starte IP-Sammlung
	print("🕵️ Kein Host gefunden. Starte IP-Sammlung...")
	lobby_started = true
	search_start_time = Time.get_ticks_msec()
	retry_timer = 1
	found_ips = []
	own_ip = _get_own_ip()
	print("🧠 Eigene IP: ", own_ip)

func _get_own_ip() -> String:
	for ip in IP.get_local_addresses():
		if ip.begins_with("172."):
			return ip
	return ""

func _process(delta):
	# Host antwortet auf Anfrage
	if is_host and udp.get_available_packet_count() > 0:
		var pkt = udp.get_packet().get_string_from_utf8()
		if pkt == "ARE_YOU_HOST":
			print("🟢 Antwort: I_AM_HOST")
			var responder := PacketPeerUDP.new()
			responder.set_dest_address(udp.get_packet_ip(), udp_port + 1)
			responder.put_packet("I_AM_HOST".to_utf8_buffer())

	if not lobby_started:
		return

	# IP-Sammlung von Clients
	if udp.get_available_packet_count() > 0:
		var pkt = udp.get_packet().get_string_from_utf8()
		if pkt == "LOBBY_REQUEST":
			var ip = udp.get_packet_ip()
			if ip != own_ip and ip not in found_ips:
				found_ips.append(ip)
				print("📥 Neue IP entdeckt:", ip)

	retry_timer += delta
	if retry_timer >= 1:
		retry_timer = 0
		udp.put_packet("LOBBY_REQUEST".to_utf8_buffer())
		print("📤 UDP-Broadcast gesendet")

	var elapsed = Time.get_ticks_msec() - search_start_time
	if elapsed > 10000:
		found_ips.append(own_ip)
		found_ips.sort()
		var selected_host = found_ips[0]
		lobby_started = false

		if selected_host == own_ip:
			print("🧑‍💼 Ich bin der Host:", own_ip)
			_start_as_host()
		else:
			print("🔗 Verbinde als Client zu:", selected_host)
			_connect_as_client(selected_host)

	# Host synchronisiert Lobby
	if is_host:
		sync_timer += delta
		if sync_timer >= 1.0:
			sync_timer = 0
			_sync_lobby_with_all()

func _start_as_host():
	is_host = true
	var peer = ENetMultiplayerPeer.new()
	peer.create_server(12345)
	multiplayer.multiplayer_peer = peer
	GameState.player_list = []
	_register_self()
	# Eigene Stimme übermitteln (Host zählt mit!)
	GameState.player_votes[GameState.player_name] = {
		"film": GameState.selected_film,
		"scene": GameState.selected_scene
	}
	_update_votes()
	print("🚀 Host gestartet")

func _connect_as_client(ip):
	is_host = false
	var peer = ENetMultiplayerPeer.new()
	var result = peer.create_client(ip, 12345)
	if result != OK:
		print("❌ Verbindung fehlgeschlagen")
		return
	multiplayer.multiplayer_peer = peer
	await multiplayer.connected_to_server
	print("🔗 Verbunden mit Host")

	GameState.host_ip = ip
	print("Host-IP gespeichert: ", GameState.host_ip)

	rpc_id(1, "register_player", GameState.player_name)
	rpc_id(1, "submit_vote", GameState.player_name, GameState.selected_film, GameState.selected_scene)

@rpc("any_peer")
func register_player(name):
	if is_host:
		var id = multiplayer.get_remote_sender_id()
		peer_to_name[id] = name
		GameState.player_list.append({"name": name, "ready": false})
		_sync_lobby_with_all()

func _sync_lobby_with_all():
	rpc("update_player_list", GameState.player_list)

@rpc("authority")
func update_player_list(new_list):
	GameState.player_list = new_list
	var path = "/root/Node3D/MenuPlane/CanvasLayer"
	if has_node(path):
		get_node(path).update_lobby_ui()

@rpc("any_peer")
func set_ready_status(player_name, ready_state):
	if is_host:
		for player in GameState.player_list:
			if player.name == player_name:
				player.ready = ready_state
				break
		_sync_lobby_with_all()

func _register_self():
	GameState.player_list.append({"name": GameState.player_name, "ready": false})
	_sync_lobby_with_all()

func _on_peer_disconnected(id):
	if is_host and peer_to_name.has(id):
		var name = peer_to_name[id]
		peer_to_name.erase(id)
		GameState.player_list = GameState.player_list.filter(func(p): return p.name != name)
		print("❌ Spieler getrennt:", name)
		_sync_lobby_with_all()

@rpc("any_peer")
func submit_vote(player_name: String, film_name: String, scene_name: String):
	if is_host:
		GameState.player_votes[player_name] = {
			"film": film_name,
			"scene": scene_name
		}
		_update_votes()
		print("🗳️ Stimme von", player_name, "für", film_name, "/", scene_name)

func _update_votes():
	GameState.film_votes.clear()
	GameState.scene_votes.clear()
	for vote in GameState.player_votes.values():
		var film = vote["film"]
		var scene = vote["scene"]
		GameState.film_votes[film] = GameState.film_votes.get(film, 0) + 1
		GameState.scene_votes[scene] = GameState.scene_votes.get(scene, 0) + 1

func evaluate_vote_results():
	if not is_host:
		return

	var film = _get_majority(GameState.film_votes)
	var scene = _get_majority(GameState.scene_votes)

	GameState.voted_film = film
	GameState.voted_scene = scene

	print("✅ Ausgewertet: ", film, "/", scene)

	# Ergebnis an alle Clients senden
	rpc("receive_vote_result", film, scene)

	# Auch lokal beim Host anzeigen
	if has_node("/root/CanvasLayer"):
		get_node("/root/CanvasLayer").show_menu("ControlFinalStart")
		get_node("/root/CanvasLayer").update_final_result()

func _get_majority(vote_dict: Dictionary) -> String:
	var max_votes = 0
	var winners = []
	for option in vote_dict.keys():
		var count = vote_dict[option]
		if count > max_votes:
			max_votes = count
			winners = [option]
		elif count == max_votes:
			winners.append(option)
	return winners[randi() % winners.size()]

@rpc("authority")
func receive_vote_result(film, scene):
	GameState.voted_film = film
	GameState.voted_scene = scene
	print("📨 Ergebnis empfangen:", film, "/", scene)
	var path = "/root/Node3D/MenuPlane/CanvasLayer"
	if has_node(path):
		get_node(path).update_final_result()
		
@rpc("authority" ,"call_local")
func start_film_for_all(scene: String):
	print("🎬 Starte Szene für alle:", scene)
	match scene:
		"MixedReality":
			get_tree().change_scene_to_file("res://mixed_reality.tscn")
		"KinoVR":
			get_tree().change_scene_to_file("res://Kino.tscn")
		"WohnzimmerVR":
			get_tree().change_scene_to_file("res://Wohnizimmer.tscn")
