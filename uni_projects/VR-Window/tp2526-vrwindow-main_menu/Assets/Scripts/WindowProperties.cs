using UnityEngine;

public class WindowProperties : MonoBehaviour
{
    //Bottom-left, Bottom-right top-left, top-right corners of plane respectively
    public Vector3 TopLeft { get; private set; }
    public Vector3 TopRight { get; private set; }
    public Vector3 BottomLeft { get; private set; }
    public Vector3 BottomRight { get; private set; }

    public float GizmoRadius = 0.05f;

    // Debug: visualize corners in editor
    private void OnDrawGizmos()
    {
        UpdateCornerPositions();
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(TopLeft, GizmoRadius);
        Gizmos.color = Color.green;
        Gizmos.DrawSphere(TopRight, GizmoRadius);
        Gizmos.color = Color.blue;
        Gizmos.DrawSphere(BottomRight, GizmoRadius);
        Gizmos.color = Color.yellow;
        Gizmos.DrawSphere(BottomLeft, GizmoRadius);
    }

    void UpdateCornerPositions()
    {
        BottomLeft  = transform.TransformPoint(new Vector3(-0.5f, -0.5f, 0f));
        BottomRight = transform.TransformPoint(new Vector3( 0.5f, -0.5f, 0f));
        TopLeft     = transform.TransformPoint(new Vector3(-0.5f,  0.5f, 0f));
        TopRight    = transform.TransformPoint(new Vector3( 0.5f,  0.5f, 0f));
    }

    void Update()
    {
        UpdateCornerPositions();
    }
    
}
