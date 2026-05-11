using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Transfer pose of "tracker" from tracking space to this transform in Unity world space.  
/// </summary>
public class ApplyCoordinateSystemTransform : MonoBehaviour
{
    public Transform tracker;
    public Transform windowCoordinateSystem;

    void Update()
    {
        if(!tracker || !WindowCalibration.Instance.isCalibrated) return;

        // vr -> window_real
        Matrix4x4 vrToWindow = WindowCalibration.Instance.VRToWindowMatrix;

        // window_virtual -> unity_global
        Vector3 tmp_scale = windowCoordinateSystem.localScale;
        // windowCoordinateSystem.localScale = new Vector3(1, 1, 1);
        Matrix4x4 windowToUnity = windowCoordinateSystem.localToWorldMatrix;
        windowCoordinateSystem.localScale = tmp_scale;

        // move this object to tracker virtual pose equivalent in relation to window
        Matrix4x4 poseTransformScene = windowToUnity * vrToWindow;

        // apply translation
        transform.position = poseTransformScene.MultiplyPoint3x4(tracker.position);

        // Optional: align object to face the window (so its forward points away from the window)
        transform.rotation = Quaternion.LookRotation(
            poseTransformScene.MultiplyVector(tracker.forward).normalized, 
            poseTransformScene.MultiplyVector(tracker.up).normalized
        );
    }
}
