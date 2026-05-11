---
title: Technical Architecture Overview
---

# Technical Architecture Overview

## Calibration

• During calibration the user aligns the real-world projection window with the virtual scene in Unity.

• The user determines the positions of the four corners of the physical projection window in the coordinate system of the VR tracking hardware.

• To do so, the user first places the tracker in the top left corner, presses enter, and proceeds to do the same with the top right and bottom left corners. The fourth corner is calculated afterwards using those 3 positions.

• These corner positions define a coordinate system called window_real.

• The origin of window_real is located at the lower left corner of the window.

• The coordinate convention is:\
x = right\
y = up\
z = towards the observer

• A 4x4 transformation matrix is calculated to convert positions from the VR tracking coordinate system into the window_real coordinate system.

• This matrix remains static during gameplay and defines the spatial relationship between the tracking system and the projection window.

• The real width and height of the window are also determined during calibration.

• Tracked objects such as the observer tracker and the VR player can then be converted into the calibrated coordinate system.

---

## Projection

• A virtual window (window_virtual) is created inside the Unity scene to represent the real projection surface.

• The size and orientation of window_virtual are matched to the calibrated dimensions of the real window.

• The maze environment is rendered behind this window to create the illusion of looking into a virtual world.

• The observer's tracked position is used to determine the correct viewing perspective.

• Off-axis projection is applied so that the rendered perspective changes depending on the observer's position.

• The camera projection matrix is updated dynamically based on the observer’s position relative to the window.

• This allows the projected scene to appear geometrically correct when viewed from different angles.

---

## Tracking and Input

• The users interact with the game using VR tracking hardware (HTC Vive trackers).

• The VR player navigates inside the maze using a VR headset.

• Player movement is controlled using a joystick instead of keyboard input.

• The joystick provides directional input for navigating through the maze.

• The second user acts as an observer and carries a tracker in the real world.

• The observer’s tracker position is mapped into the virtual world.

• This tracker controls a light source inside the maze.

• The light reveals parts of the maze and helps guide the VR player.

• Tracking data and joystick input are continuously processed during gameplay.

---

## Game Integration

• The game is designed as a cooperative two-player experience.

• One user is the VR player navigating through the maze.

• The second user is the observer who guides the VR player using a tracked light source.

• The difficulty increases across three levels.

Level 1\
• The maze is partially visible but still dim.\
• The observer’s light helps reveal additional paths and guide the VR player to the exit.

Level 2\
• The maze becomes darker, making navigation more difficult.\
• The VR player must collect keys before reaching the exit.\
• The observer continues to guide the player using the light.

Level 3\
• The VR player must collect keys while escaping from a monster that searches the maze.\
• The maze remains dark, increasing the challenge.\
• If the monster catches the VR player, the game is lost.\
• If all keys are collected and the player reaches the exit, the players win.

## Program Control Flow

The program flow is event-driven and controlled primarily by the `GameManager`. Player interactions (e.g. trigger collisions) and continuous update loops determine state transitions such as level progression, enemy behavior, and UI changes.

---

### Level Loading

When the player enters the exit door trigger, `MazeExit.cs` detects the collision via `OnTriggerEnter()` and invokes `GameManager.increaseLvl()`.\
This increments the current level and calls the corresponding method (`GoToLevel1()`, `GoToLevel2()`, `GoToLevel3()`), which regenerates the maze using `GridMazeGenerator.GenerateMaze()`.

---

### Key Collection & Door Unlock

Each key has a trigger collider. When collected, `Key.cs → OnTriggerEnter()` invokes `GameManager.AddKey()`, incrementing `keysCollected`.

In `GameManager.Update()`, the condition `keysCollected >= 3` is checked every frame.\
If true (in Level 2 and Level 3), `SpawnExitDoor()` is invoked, placing and activating the exit door at the maze exit.

---

### Monster Spawn & Chase

At the start of Level 3, `GoToLevel3()` invokes `SpawnMonster()`, instantiating the monster prefab.

The monster behavior is controlled by `GridMonster.Update()`, which executes every frame.\
Movement is determined using `PickBestTile()`, allowing the monster to navigate toward the player while avoiding previously visited tiles.

---

### Death / Game Over

If the monster reaches the player (distance \< 0.5 units, checked in `GridMonster.Update()`), `CatchPlayer()` is triggered.

This invokes `GameManager.GameOver()`, which:

- freezes the game (`Time.timeScale = 0`)
- activates the `gameOverPanel` UI

---

### Win Condition

When the player exits Level 3, `GameManager.increaseLvl()` increases the level beyond 3, triggering `WinGame()`.

This:

- freezes the game
- activates the `winPanel` UI

---

### Window Projection

At startup, `ActivateAllDisplays.cs` enables the secondary display for the Window Player.

`OffAxisPerspectiveProjection.cs` computes the projection matrix every frame based on physical window corners provided by `WindowProperties.cs`.

Projection warping is handled by `HomographyController.cs` and applied via `HomographyWarpFeature.cs` as a post-processing effect.