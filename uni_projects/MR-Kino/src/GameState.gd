extends Node

# === Spielerinformationen (lokal) ===
var player_name: String = ""              # Dein Spielername
var selected_film: String = ""            # Deine Filmwahl
var selected_scene: String = ""           # Deine Szenenwahl

# === Netzwerkstatus ===
var host_ip: String = ""                  # Host-IP, vom Client gespeichert

# === Spielerliste mit Namen und Bereit-Status ===
var player_list: Array = []               # [{"name": "Anna", "ready": true}, ...]

# === Vom Server geladene Filme ===
var available_films: Array = []           # z. B. ["Avatar", "Matrix"]

# === Stimmen der Spieler (gesendet vom Client an den Host) ===
# {"Anna": {"film": "Avatar", "scene": "MixedReality"}, ...}
var player_votes: Dictionary = {}

# === Zähler für jede Stimme zur Mehrheitsauswertung ===
var film_votes: Dictionary = {}           # z. B. {"Avatar": 2, "Matrix": 1}
var scene_votes: Dictionary = {}          # z. B. {"MixedReality": 2, "KinoVR": 1}

# === Finale Auswahl durch Host per Mehrheitsentscheid ===
var voted_film: String = ""               # Ergebnisfilm
var voted_scene: String = ""              # Ergebnisszene
