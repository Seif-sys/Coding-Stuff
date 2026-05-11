1. Steam VR installation
2. https://github.com/ViveSoftware/VIVE-OpenXR-Unity/tree/master/Installer install package
3. Package in Unity reinpacken.
4. add the profile in Assets>import package>custom package
5. update vive xr in unity : vive>openxr installer>install or update
6. edit>project settings >xr plug-in>openxr - add the following: 
    - htc vive tracker profile
    - htc vive controller profile

To import window data in different scripts:

```
using UnityEngine;

public class UseCalibration : MonoBehaviour
{
    void Update()
    {
        // Example: take this object position and convert it to window coordinates
        Vector3 worldPoint = transform.position;

        Vector3 windowPoint = WindowCalibration.VRToWindowMatrix.MultiplyPoint3x4(worldPoint);

        Debug.Log("Window coords: " + windowPoint);
        Debug.Log("Width: " + WindowCalibration.WindowWidth);
        Debug.Log("Height: " + WindowCalibration.WindowHeight);
    }
}
```