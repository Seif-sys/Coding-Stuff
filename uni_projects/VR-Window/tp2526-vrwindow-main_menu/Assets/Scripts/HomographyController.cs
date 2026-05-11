using UnityEngine;
using Geometry;

[ExecuteAlways]
public class HomographyController : MonoBehaviour
{
    public Material warpMat;
    public RectTransform[] handles;   // TL, TR, BR, BL

    // TODO: implement persisting handle positions for next session (with some hysteresis or by key press, to avoid saving every frame)
    // TODO: implement loading saved handle positions on press of 'L' key 

    public RectTransform referenceRect;

    void LateUpdate()
    {
        if (warpMat == null) return;
        if (handles == null || handles.Length != 4) return;
        if (referenceRect == null) return;

        // Source points (unit square)
        (double x, double y)[] src = new (double, double)[4];
        src[0] = (0, 1);   // TL
        src[1] = (1, 1);   // TR
        src[2] = (1, 0);   // BR
        src[3] = (0, 0);   // BL

        // Destination = handles → convert to UV (0–1) inside referenceRect
        (double u, double v)[] dst = new (double, double)[4];

        for (int i = 0; i < 4; i++)
        {
            Vector2 local;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(
                referenceRect,
                RectTransformUtility.WorldToScreenPoint(null, handles[i].position),
                null,
                out local
            );

            double u = (local.x / referenceRect.rect.width) + 0.5;
            double v = (local.y / referenceRect.rect.height) + 0.5;

            dst[i] = (u, v);
        }
        // Debug.Log($"Dst UVs: {dst[0]}, {dst[1]}, {dst[2]}, {dst[3]}");

        // Compute H (3x3 double array)
        double[,] H = Homography.From4Points(src, dst);   // :contentReference[oaicite:0]{index=0}

        // Convert H → Matrix4x4
        Matrix4x4 M = Matrix4x4.identity;
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                M[r, c] = (float)H[r, c];

        // Compute inverse homography (needed by shader)
        Matrix4x4 Hinv = M.inverse;

        // Send to shader
        warpMat.SetMatrix("_HInv", Hinv);
    }
}
