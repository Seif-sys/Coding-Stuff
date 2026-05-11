<table>
<tr>
<th>Name</th>
<th>Contribution</th>
</tr>
<tr>
<td>Lucian Lohse</td>
<td>

* setup unity to render Homographie / UI-elements (cam for screen 2 and img with texture)
* integration and bug fixes after merging team results

</td>
</tr>
<tr>
<td>Yasmine Slimane</td>
<td>

* Integrated visual key asset for Level 2.
* Replaced placeholder monster with animated 3D model in Level 3.
* Set up and debugged monster animation within existing AI system.
* Refactored exit logic to replace wall object with a door prefab upon activation
* Ensured proper alignment, scaling, and trigger functionality of the door system.
* Integrated the player visual representation so the character is visible from observer viewpoints.
* Supported the merging phase by helping integrate different team members’ features into the main project.
* Participated in the testing phase, identifying and fixing issues related to object placement, animations, and gameplay flow.
</td>
</tr>
<tr>
<td>Dhouha Khalfalli Ep Ghannouchi</td>
<td>

* Contributed in the implementation of the _OffAxisPerspectiveProjection.cs_ by regulating the translation operations to adapt to the perceivers position.
* Implemented a multi-level procedural maze system, generating dynamic grid-based labyrinths for Level 2 and Level 3 using a depth-first search algorithm with optional random seed configuration.
* Engineered a progressive level transition framework, establishing logical connections between <br>
  Level 1 → Level 2 → Level 3, including controlled state resets and runtime maze regeneration.
* Designed and integrated a key-collection mechanic for Level 2, spawning three randomized key objects within the maze grid and linking collection milestones to exit activation logic.
* Developed a dynamic exit-wall system for Level 2, assigning a randomized border wall as the level exit and activating it only after the required key threshold is reached, including visual emission feedback and collider-state transitions.
</td>
</tr>
<tr>
<td>Seif Saad</td>
<td>

* Implemented OffAxisPerspectiveProjection.cs from the ground up, including the full mathematical pipeline for dynamically regulating the viewing window to achieve a convincing parallax effect. This involved deriving and applying matrix and vector calculations based on the three corners of the virtual window, ensuring the projection adapts fluidly and in real time to the perceiver's changing angle and position.
* Collaborated with team members in the early stages of the project to establish the core game concept, contributing ideas around the overall design direction, player experience, and technical feasibility of key mechanics.
* Contributed to the design and implementation of the maze exit mechanic, helping define the logic and conditions that trigger level progression. Additionally, implemented dummy XR Origin controls to facilitate early-stage testing and interaction before full VR hardware integration was in place.
* Integrated the off-axis projection window directly into the maze scene, creating a dynamic "helicopter view" that serves as a live, perspective-shifted overview of the environment. The projection's angle and framing update continuously based on the perceiver's real-world position, creating a seamless link between physical movement and in-game perspective.
* Conducted hands-on testing of HTC Vive controller mapping for the VR player within the maze scene, verifying input bindings, interaction responses, and ensuring controller behavior aligned with the intended player experience.
* Reimplemented the transition system between levels, overhauling the logic to ensure smoother state changes. This also included reworking the ambient lighting system so that light conditions shift appropriately as the player moves between different stages of the game.
* Contributed to diagnosing and resolving a persistent collision detection problem, working with the team to identify the root cause and apply a stable fix that preserved intended player movement boundaries.
* Regulated and fine-tuned the Spotlight settings for the camera, adjusting intensity, range, angle, and falloff to ensure visually consistent and well-lit scenes across different viewing conditions.
* Redesigned the overall scene architecture so that the entire game runs within a single unified scene rather than across multiple discrete scenes. This significantly reduced load times, eliminated transition artifacts, and resulted in a much smoother overall player experience.
* Identified and fixed a controller-related bug where the camera (rather than the player body) was being treated as the subject of movement. This produced the illusion of broken or misaligned collision, and resolving it restored physically coherent movement and proper interaction with the environment.
* Conducted comprehensive end-to-end testing of all implemented features in preparation for the final version, systematically identifying bugs, inconsistencies, and edge cases across both the VR and non-VR components of the project.
</td>
</tr>
<tr>
<td>Hadil Ghedir</td>
<td>

* Implemented audio feedback for gameplay events by integrating a sound effect triggered when the monster captures the player using Unity’s AudioSource component
* Developed a background music system for gameplay levels, enabling continuous looping audio during gameplay.
* Designed and implemented a dynamic music switching mechanism between Level 2 and Level 3, allowing different soundtracks within the same scene.
* Integrated and configured audio assets within Unity, including importing and preparing sound files for runtime usage.
* Contributed to branch integration and final project merging to combine team developments into the final version of the game.
</td>
</tr>
<tr>
<td>Mohammad Khatib</td>
<td>

* Assisting with merging multiple branches.
* Resolving existing bugs such as collisions, VR player visibility, material adjustments, and tracker connection issues.
* Creating a main menu for the game that showcases the project's mechanics.
* Connecting the trackers with SteamVR and Unity and resolving all related connection issues.
* Proposing the maze concept and explaining how the mechanics used in the project can be applied to it.
* Determining the positions of the window corners in the VR hardware coordinate system.
* Calculating the 4×4 transformation matrix from the VR tracking system to `window_real` (where the `window_real` origin is the lower-left corner, following the Unity coordinate convention: x = right, y = up, z = forward). This allows tracked positions of the observer or VR player to be expressed relative to `window_real`.
* Exposing the real width and height of the window, along with the transformation matrix (both static and unchanged during gameplay).
* Exposing tracked positions of the observer tracker and VR player tracker in the `window_real` coordinate system.
</td>
</tr>
<tr>
<td>Mohamed Sabri Jlizi</td>
<td>

* Contributed to the hardware setup and testing process, including integrating, configuring, and validating the VR tracker and controllers within the Unity game engine.
* Replaced the legacy WASD keyboard movement with HTC Vive controller-based locomotion using OpenXR and the XR Interaction Toolkit, enabling immersive and natural navigation within the virtual environment.
* Implemented a 4×4 transformation matrix–based VR tracking system to map tracked positions into the window_real coordinate space (origin at the lower-left; Unity convention: x-right, y-up, z-forward), allowing precise localization of the observer/VR player relative to the physical window.
* Exposed the physical window’s real-world width and height together with the transformation matrix .
* Developed the procedural maze generator script used to construct the navigable environment.
* Co-defined the core game concept and interaction design in collaboration with other team members.
</td>
</tr>
<tr>
<td>Ibrahim Yassin</td>
<td>

* Implemented the grid-based monster AI, including tile-to-tile movement logic, player detection, and autonomous hunting behaviors.
* Designed the Game Over and Win-State logic, connecting monster interaction and key-collection milestones to the final UI and exit triggers.
* Engineered a state-persistent Game Loop system, implementing distinct Victory and Defeat UI panels with context-aware navigation that allows users to either retry the current level or restart the full application using specific input mappings.
* Synchronized monster and player interactions, ensuring the "Catch" logic correctly pauses the game engine and displays relevant feedback to the player.
</td>
</tr>
<tr>
<td>Mohamed Yazan Bido</td>
<td>

* The process of connecting the hardware Setup (Trackers, etc.) within Unity game engine including testing and configuration.
* Assisted with the integration of hardware into SteamVR and Unity.
* Determine positions of the window corners (in coordinate system of VR hardware)
* Calculate transformation matrix (4x4) VR tracking system -\> window_real (window_real origin is lower left corner, with unity coordinate convention, x=right, y=up, z=font). This allows us to know where a tracked position of observer or VR player is in relation to the window_real.
* Expose real width and height of the window, along with transformation matrix (both static, not changing during the game)
* Expose tracked positions of observer tracker, (and VR player tracker) in coordinate system of window_real.
* Supported branch merging and helped identify and resolve several bugs.
</td>
</tr>
<tr>
<td>Salem Gmiza</td>
<td>

* Conducted research during the initial phase on VR hardware setup and head-tracking integration with Unity.
* Implemented the **Tutorial Level** on the **`Tutorial_level` branch** (including key, simple monster and exit mechanisms)
</td>
</tr>
<tr>
<td>Syrine Maghzaoui</td>
<td>

Projektorkalibrierung und Homographie-Setup

* Implementierung der interaktiven Eckpunktsteuerung (Corner Handles) zur Kalibrierung der Projektionsfläche
* Entwicklung und Integration des CornerHandle-Skripts für alle vier Fensterecken (TL, TR, BR, BL)
* Konfiguration und Verknüpfung der vier Handles im HomographyController
* Einrichtung des Reference Rect zur korrekten Zuordnung der Projektionsfläche
* Implementierung der UI-Struktur für die Kalibrierung
* Canvas-Konfiguration auf Screen Space – Overlay
* Integration von EventSystem und GraphicRaycaster für die Interaktion
* Vorbereitung der Homographie-Struktur zur perspektivischen Korrektur der Projektion

Systemintegration und Fehlerbehebung

* Analyse und Behebung von Collision-Problemen im Maze-Level, bei denen der Spieler durch Wände laufen konnte
* Anpassung der Collider- und Unity-Physics-Einstellungen zur Stabilisierung der Spielerinteraktion
* Unterstützung bei der Integration der einzelnen Systemkomponenten und bei projektweiten technischen Problemen

Dokumentation und Abschlusspräsentation

* Erstellung der gesamten Abschlusspräsentation des Projekts
* Strukturierung und Aufbereitung der technischen Inhalte und Ergebnisse für die finale Projektvorstellung
* Wrote the Technical Architecture Overview section in the project wiki.
    * Documented the architecture including calibration, projection, tracking and input, and game integration.
    * Added explanations of how tracker data, joystick input, and gameplay mechanics are integrated into the system.

</td>
</tr>
</table>

