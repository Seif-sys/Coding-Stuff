@tool
class_name XRToolsStartXR
extends Node


signal xr_started
signal xr_ended
signal xr_failed_to_initialize
static var _xr_active : bool = false
@export var viewport : Viewport
@export var render_target_size_multiplier : float = 1.0
@export var enable_passthrough : bool = false: set = _set_enable_passthrough
@export var physics_rate_multiplier : int = 1
@export var target_refresh_rate : float = 0

var xr_interface : XRInterface

var xr_frame_rate : float = 0

var _webxr_session_query : bool = false


func _ready() -> void:
	if !Engine.is_editor_hint():
		_initialize()


func _initialize() -> bool:
	xr_interface = XRServer.find_interface('OpenXR')
	if xr_interface:
		return _setup_for_openxr()

	xr_interface = XRServer.find_interface('WebXR')
	if xr_interface:
		return _setup_for_webxr()

	xr_interface = null
	print("No XR interface detected")
	xr_failed_to_initialize.emit()
	return false


func end_xr() -> void:
	if xr_interface is WebXRInterface:
		xr_interface.uninitialize()
		return

	get_tree().quit()


static func is_xr_active() -> bool:
	return _xr_active


func get_xr_viewport() -> Viewport:
	if viewport:
		return viewport

	return get_viewport()


func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()

	if physics_rate_multiplier < 1:
		warnings.append("Physics rate multiplier should be at least 1x the HMD rate")

	return warnings


func _setup_for_openxr() -> bool:
	print("OpenXR: Configuring interface")

	xr_interface.render_target_size_multiplier = render_target_size_multiplier

	if not xr_interface.is_initialized():
		print("OpenXR: Initializing interface")
		if not xr_interface.initialize():
			push_error("OpenXR: Failed to initialize")
			xr_failed_to_initialize.emit()
			return false

	xr_interface.connect("session_begun", _on_openxr_session_begun)
	xr_interface.connect("session_visible", _on_openxr_visible_state)
	xr_interface.connect("session_focussed", _on_openxr_focused_state)

	if enable_passthrough and xr_interface.is_passthrough_supported():
		enable_passthrough = xr_interface.start_passthrough()

	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)

	get_xr_viewport().transparent_bg = enable_passthrough
	get_xr_viewport().use_xr = true

	return true


func _on_openxr_session_begun() -> void:
	print("OpenXR: Session begun")

	_set_xr_frame_rate()


func _on_openxr_visible_state() -> void:
	if _xr_active:
		print("OpenXR: XR ended (visible_state)")
		_xr_active = false
		xr_ended.emit()


func _on_openxr_focused_state() -> void:
	if not _xr_active:
		print("OpenXR: XR started (focused_state)")
		_xr_active = true
		xr_started.emit()


func _set_enable_passthrough(p_new_value : bool) -> void:
	enable_passthrough = p_new_value

	if xr_interface:
		if enable_passthrough:
			enable_passthrough = xr_interface.start_passthrough()
		else:
			xr_interface.stop_passthrough()

		get_xr_viewport().transparent_bg = enable_passthrough


# Perform WebXR setup
func _setup_for_webxr() -> bool:
	print("WebXR: Configuring interface")

	# Connect the WebXR events
	xr_interface.connect("session_supported", _on_webxr_session_supported)
	xr_interface.connect("session_started", _on_webxr_session_started)
	xr_interface.connect("session_ended", _on_webxr_session_ended)
	xr_interface.connect("session_failed", _on_webxr_session_failed)

	# If the viewport is already in XR mode then we are done.
	if get_xr_viewport().use_xr:
		return true

	# This returns immediately - our _webxr_session_supported() method
	# (which we connected to the "session_supported" signal above) will
	# be called sometime later to let us know if it's supported or not.
	_webxr_session_query = true
	xr_interface.is_session_supported('immersive-ar' if enable_passthrough else 'immersive-vr')

	# Report success
	return true


# Handle WebXR session supported check
func _on_webxr_session_supported(session_mode: String, supported: bool) -> void:
	# Skip if not running session-query
	if not _webxr_session_query:
		return

	# Clear the query flag
	_webxr_session_query = false

	# Report if not supported
	if not supported:
		OS.alert("Your web browser doesn't support " + session_mode + ". Sorry!")
		xr_failed_to_initialize.emit()
		return

	# WebXR supported - show canvas on web browser to enter WebVR
	$EnterWebXR.visible = true


# Called when the WebXR session has started successfully
func _on_webxr_session_started() -> void:
	print("WebXR: Session started")

	# Set the XR frame rate
	_set_xr_frame_rate()

	# Hide the canvas and switch the viewport to XR
	$EnterWebXR.visible = false
	get_xr_viewport().transparent_bg = enable_passthrough
	get_xr_viewport().use_xr = true

	# Report the XR starting
	_xr_active = true
	xr_started.emit()


# Called when the user ends the immersive VR session
func _on_webxr_session_ended() -> void:
	print("WebXR: Session ended")

	# Show the canvas and switch the viewport to non-XR
	$EnterWebXR.visible = true
	get_xr_viewport().transparent_bg = false
	get_xr_viewport().use_xr = false

	# Report the XR ending
	_xr_active = false
	xr_ended.emit()


# Called when the immersive VR session fails to start
func _on_webxr_session_failed(message: String) -> void:
	OS.alert("Unable to enter VR: " + message)
	$EnterWebXR.visible = true


# Handle the Enter VR button on the WebXR browser
func _on_enter_webxr_button_pressed() -> void:
	# Configure the WebXR interface
	xr_interface.session_mode = 'immersive-ar' if enable_passthrough else 'immersive-vr'
	xr_interface.requested_reference_space_types = 'bounded-floor, local-floor, local'
	xr_interface.required_features = 'local-floor'
	xr_interface.optional_features = 'bounded-floor'

	# Add hand-tracking if enabled in the project settings
	if ProjectSettings.get_setting_with_override("xr/openxr/extensions/hand_tracking"):
		xr_interface.optional_features += ", hand-tracking"

	# Initialize the interface. This should trigger either _on_webxr_session_started
	# or _on_webxr_session_failed
	if not xr_interface.initialize():
		OS.alert("Failed to initialize WebXR")


func _set_xr_frame_rate() -> void:
	xr_frame_rate = xr_interface.get_display_refresh_rate()
	if xr_frame_rate > 0:
		print("StartXR: Refresh rate reported as ", str(xr_frame_rate))
	else:
		print("StartXR: No refresh rate given by XR runtime")

	var desired_rate := target_refresh_rate if target_refresh_rate > 0 else xr_frame_rate
	var available_rates : Array = xr_interface.get_available_display_refresh_rates()
	if available_rates.size() == 0:
		print("StartXR: Target does not support refresh rate extension")
	elif available_rates.size() == 1:
		print("StartXR: Target supports only one refresh rate")
	elif desired_rate > 0:
		print("StartXR: Available refresh rates are ", str(available_rates))
		var rate = _find_closest(available_rates, desired_rate)
		if rate > 0:
			print("StartXR: Setting refresh rate to ", str(rate))
			xr_interface.set_display_refresh_rate(rate)
			xr_frame_rate = rate

	var active_rate := xr_frame_rate if xr_frame_rate > 0 else 144.0
	var physics_rate := int(round(active_rate * physics_rate_multiplier))
	print("StartXR: Setting physics rate to ", physics_rate)
	Engine.physics_ticks_per_second = physics_rate


func _find_closest(values : Array, target : float) -> float:
	if values.size() == 0:
		return 0.0

	var best : float = values.front()
	for v in values:
		if abs(target - v) < abs(target - best):
			best = v

	return best
