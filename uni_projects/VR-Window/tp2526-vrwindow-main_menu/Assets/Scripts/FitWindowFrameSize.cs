using UnityEngine;

public class FitWindowSize : MonoBehaviour
{

    void Start()
    {
        WindowCalibration.Instance.OnCalibrationFinished += ResizeWindow;
    }

    void ResizeWindow()
    {
        this.transform.localScale = new Vector3(WindowCalibration.Instance.windowWidth, WindowCalibration.Instance.windowHeight, 1);
        Debug.Log("Resized Window");
    }
}