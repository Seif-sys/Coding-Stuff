# Overview

In `Scenes/` there are three scenes to make getting started easier.

## Team A - Projektorkalibrierung

Scene `Test_ProjectorHomography.scene` contains a virtual version of our real-life setup - a "digital twin" so to speak.
The goal here is to project the image of a camera undistorted onto the "window".
The following elements are already implemented:
- Placeholder UI elements for the "corner handles". They are not interactive yet.
- An additional blit render pass that is executed after the normal rendering. It applies an inverse homography that is given to the material `HomopraphyWarpMat` (see `Scripts/HomographyController.cs`).
- A Camera that renders into a square RenderTexture and uses the additional blit render pass.
- A Projector that projects the RenderTexture onto the window.


## Team B - Tracking

Scene `Test_Tracking.scene` contains a placeholder version of objects that we need to be tracked:
- virtual "observer camera" (position)
- window (position of the corners)
- vr player (position and orientation)


## Team C - Projektorkalibrierung (my team)

Scene `Test_OffAxisPerspectiveProjection.scene` also contains a "digital twin" of our real-life setup.
The goal here is to render the image of a virtual camera in a way that makes it look like we are looking through the "window".
For this, the following elements are already implemented:
- A "Camera" paren gameobject, combining the camera that is rendered onto the window ("RenderTexture Camera") and an observer camera (Main Camera) demonstrating what an observer would see (shown in the preview). Move this parent object (not the separate camera child objects) to simulate and test the parallax viewing effect.
- The "RenderTexture Camera" holds a script "OffAxisPerspectiveProjection.cs" that provides a framework for setting a custom projection and view (w2c) matrix for its rendering.
- A window that shows the rendered camera image from "RenderTexture Camera". This gameobject also holds a script `WindowProperties.cs` that exposes the positions of its four corners.
