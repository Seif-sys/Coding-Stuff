using UnityEngine;
using System.Collections;

public class ActivateAllDisplays : MonoBehaviour
{
    void Start ()
    {
        Debug.Log ("displays connected: " + Display.displays.Length);
        // Display.displays[0] is the primary, default display and is always ON
        // This will be used for the VR HMD
    
        // Additionally activate the second display for the window (projector)
        if (Display.displays.Length > 1)
            Display.displays[1].Activate();
        else
            Debug.LogWarning("No second display found for window/projector!");
    }
}
