using UnityEngine;
using UnityEngine.Rendering;

[ExecuteAlways]
[DefaultExecutionOrder(-1000)]
public class OffAxisPerspectiveProjection : MonoBehaviour
{
    public WindowProperties window;
    public Vector2Int projectorResolution = new Vector2Int(3840, 2160);

    void OnEnable()
    {
        RenderPipelineManager.beginCameraRendering += OnBeginCameraRendering;
        RenderPipelineManager.endCameraRendering   += OnEndCameraRendering;
    }
    void OnDisable()
    {
        RenderPipelineManager.beginCameraRendering -= OnBeginCameraRendering;
        RenderPipelineManager.endCameraRendering   -= OnEndCameraRendering;
    }

    void OnDrawGizmos()
    {
        Camera warp_cam = GetComponent<Camera>();
        if (warp_cam == null) return;
        // visualize frustum to window corners with gizmo lines
        if (window == null) return;
        var cam_pos = warp_cam.transform.position;
        Gizmos.color = Color.red;
        Gizmos.DrawLine(cam_pos, window.TopLeft);
        Gizmos.color = Color.green;
        Gizmos.DrawLine(cam_pos, window.TopRight);
        Gizmos.color = Color.blue;
        Gizmos.DrawLine(cam_pos, window.BottomRight);
        Gizmos.color = Color.yellow;
        Gizmos.DrawLine(cam_pos, window.BottomLeft);
    }

    float GetAspectRatioLongToShort(Vector2 size)
    {
        if (size.x >= size.y)
            return size.x / size.y;
        else
            return size.y / size.x;
    }

    /// <summary>
    /// Use window size to determine aspect ratio and adjust render texture resolution accordingly
    /// to maximize effective pixel usage given the projector resolution without rendering a larger texture than needed.
    /// </summary>
    void UpdateRenderTextureResolution(RenderTexture rt, Vector2 windowSize, Vector2Int projectorResolution)
    {
        if (rt == null) return;
        float aspectWindow = GetAspectRatioLongToShort(windowSize);
        float aspectProjector = GetAspectRatioLongToShort(new Vector2(projectorResolution.x, projectorResolution.y));
        // since the window has to be covered completely by the projector (so it has to fit into the projector resolution),
        // but we don't know if the projector is used in landscape or portrait mode,
        // we only have an upper limit for the resolution 
        // given by the largest window we can fit into the projector in any orientation.
        int newWidth, newHeight;
        if (aspectWindow >= aspectProjector)
        {
            // window is wider than projector → fit width
            newWidth = projectorResolution.x;
            newHeight = Mathf.RoundToInt(projectorResolution.x / aspectWindow);
        }
        else
        {
            // window is taller than projector → fit height
            newHeight = projectorResolution.y;
            newWidth = Mathf.RoundToInt(projectorResolution.y * aspectWindow);
        }
        // apply new resolution if changed
        if (rt.width != newWidth || rt.height != newHeight)
        {
            Debug.Log("Changing RenderTexture resolution from " + rt.width + " x " + rt.height + " to " + newWidth + " x " + newHeight);
            rt.Release();
            rt.width = newWidth;
            rt.height = newHeight;
            rt.Create();
        }
    }

    void OnBeginCameraRendering(ScriptableRenderContext ctx, Camera cam)
    {
        Camera warp_cam = GetComponent<Camera>();
        if (cam != warp_cam) return;

        if (window == null) return;

        UpdateRenderTextureResolution(
            cam.targetTexture, 
            new Vector2(window.transform.localScale.x, window.transform.localScale.y),
            projectorResolution);

        // 1) Fenster-Ecken (Welt)
        Vector3 pa = window.BottomLeft;
        Vector3 pb = window.BottomRight;
        Vector3 pc = window.TopLeft;

        // 2) Auge
        Vector3 pe = warp_cam.transform.position;

        // 3) Basisvektoren
        Vector3 vr = (pb - pa).normalized;
        Vector3 vu = (pc - pa).normalized;
        Vector3 vn = Vector3.Cross(vu, vr).normalized;

        // 4) Abstand Auge → Fenster-Ebene
        float d = Vector3.Dot(vn, pa - pe);

        // Schutz: wenn Abstand fast 0 → nichts machen
        if (Mathf.Abs(d) < 0.001f)
        {
            cam.ResetProjectionMatrix();
            cam.ResetWorldToCameraMatrix();
            return;
        }

        // Normalenrichtung korrigieren
        if (d < 0f)
        {
            // Debug.LogWarning("Off-Axis Projection: Inverted window normal detected. Flipping normal.");
            vn = -vn;
            d  = -d;
        }

        float n = warp_cam.nearClipPlane;   // z.B. 0.1
        float f = warp_cam.farClipPlane;    // z.B. 100
        float nOverD = n / d;

        // 5) Off-Axis Frustum-Grenzen
        float l = Vector3.Dot(vr, pa - pe) * nOverD;
        float r = Vector3.Dot(vr, pb - pe) * nOverD;
        float b = Vector3.Dot(vu, pa - pe) * nOverD;
        float t = Vector3.Dot(vu, pc - pe) * nOverD;

        // 6) Nur Projektionsmatrix setzen
        Matrix4x4 P = Matrix4x4.Frustum(l, r, b, t, n, f);
        cam.projectionMatrix = P;

        // 7) Custom view-matrix for rotation and transformation
        Matrix4x4 M2 = new Matrix4x4();     

        M2.SetRow(0, new Vector4( vr.x, vr.y, vr.z, -Vector3.Dot(vr, pe)));
        M2.SetRow(1, new Vector4( vu.x, vu.y, vu.z, -Vector3.Dot(vu, pe)));
        M2.SetRow(2, new Vector4(-vn.x,-vn.y,-vn.z,  Vector3.Dot(vn, pe)));
        M2.SetRow(3, new Vector4( 0f,   0f,   0f,    1f));

        cam.worldToCameraMatrix = M2;
    }

    void OnEndCameraRendering(ScriptableRenderContext ctx, Camera cam)
    {
        Camera warp_cam = GetComponent<Camera>();
        if (cam == warp_cam)
        {
            cam.ResetProjectionMatrix();
            cam.ResetWorldToCameraMatrix();
        }
    }
}
