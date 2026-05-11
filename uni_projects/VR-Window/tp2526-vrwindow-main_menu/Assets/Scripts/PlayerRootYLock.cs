using UnityEngine;

public class PlayerRootYLock : MonoBehaviour
{
    private float lockedY;

    void Start()
    {
        // Store initial world Y position
        lockedY = transform.position.y;
    }

    void LateUpdate()
    {
        // Force Y back after XR has modified children
        Vector3 pos = transform.position;
        pos.y = lockedY;
        transform.position = pos;
    }
}