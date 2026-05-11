using UnityEngine;
using System.IO;
using UnityEngine.InputSystem;

[System.Serializable]
public class CalibrationData
{
    public Vector3 topLeft;
    public Vector3 topRight;
    public Vector3 bottomLeft;
}

public class WindowCalibration : MonoBehaviour
{
    // singleton pattern to access non-static variables from outside
    public static WindowCalibration Instance { get; private set; }
    private void Awake() 
    { 
        if (Instance != null && Instance != this) 
            Destroy(this); 
        else 
            Instance = this; 
    }

    public Matrix4x4 VRToWindowMatrix;
    public float windowWidth;
    public float windowHeight;
    public bool isCalibrated = false;

    public delegate void Notify();

    public event Notify OnCalibrationFinished;

    private string FilePath = Application.dataPath + "/WindowCalibration.json";
    private int clickCount = 0;

    private CalibrationData calibrationData = new CalibrationData();
    
    void Start()
    {
        // Check if the file exists, if so, give the option to load it
        if (File.Exists(FilePath))
        {
            Debug.Log("Do you want to load previous calibration data from " + FilePath + "?");
        }
        else
        {
            Debug.Log("No previous calibration data found. Starting new calibration.");
        }
    }

    void Update()
    {
        if (isCalibrated)
        {
            // Listen for 'R' key to restart calibration
            if (Input.GetKeyDown(KeyCode.R))
            {
                RestartCalibration();
            }
        }
        else
        {
            // Listen for 'S' key or 'Enter' key to record points
            if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.Return))
            {
                if (clickCount == 0)
                {
                    calibrationData.topLeft = transform.position;
                    Debug.Log("Top-Left corner recorded.");
                }
                else if (clickCount == 1)
                {
                    calibrationData.topRight = transform.position;
                    Debug.Log("Top-Right corner recorded.");
                }
                else if (clickCount == 2)
                {
                    calibrationData.bottomLeft = transform.position;
                    Debug.Log("Bottom-Left corner recorded.");
                    SaveCalibrationData(FilePath, calibrationData);
                    ComputeWindowTransform(calibrationData, out windowWidth, out windowHeight, out VRToWindowMatrix);
                    isCalibrated = true;
                    OnCalibrationFinished?.Invoke();
                }

                clickCount++;
            }

            // Listen for 'L' key to load previous calibration
            if (Input.GetKeyDown(KeyCode.L))
            {
                if (File.Exists(FilePath))
                {
                    string json = File.ReadAllText(FilePath);
                    calibrationData = JsonUtility.FromJson<CalibrationData>(json);

                    ComputeWindowTransform(calibrationData, out windowWidth, out windowHeight, out VRToWindowMatrix);
                    isCalibrated = true;
                    OnCalibrationFinished?.Invoke();

                    Debug.Log("Successfully loaded previous calibration data.");
                }
                else
                {
                    Debug.Log("No previous calibration data found to load.");
                }
            }   
        }
    }

    void RestartCalibration()
    {
        isCalibrated = false;
        clickCount = 0;
        Debug.Log("Calibration restarted. Press S 3 times: TopLeft, TopRight, BottomLeft");
    }

    // void Save(string label, Vector3 pos)
    // {
    //     string line = $"{label}: {pos}\n";
    //     File.AppendAllText(filePath, line);
    //     Debug.Log(line);
    // }

    void SaveCalibrationData(string filePath, CalibrationData calibrationData)
    {
        string json = JsonUtility.ToJson(calibrationData, true);
        File.WriteAllText(filePath, json);
        Debug.Log("Calibration data saved to " + filePath);
    }

    void ComputeWindowTransform(CalibrationData calibrationData, out float windowWidth, out float windowHeight, out Matrix4x4 VRToWindowMatrix)
    {
        Vector3 xAxis = (calibrationData.topRight - calibrationData.topLeft).normalized;
        Vector3 yAxis = (calibrationData.topLeft - calibrationData.bottomLeft).normalized;
        Vector3 zAxis = Vector3.Cross(xAxis, yAxis).normalized;
        // orthogonalize yAxis from the other two
        yAxis = Vector3.Cross(zAxis, xAxis).normalized;

        // ✅ Rounded width/height to 3 decimals
        windowWidth = Vector3.Distance(calibrationData.topRight, calibrationData.topLeft);
        windowHeight = Vector3.Distance(calibrationData.topLeft, calibrationData.bottomLeft);

        Vector3 origin = calibrationData.bottomLeft + (calibrationData.topRight - calibrationData.topLeft) * 0.5f + (calibrationData.topLeft - calibrationData.bottomLeft) * 0.5f;

        // inverse of Window to VR
        // ( nx.x, ny.x, nz.x, o.x )
        // ( nx.y, ny.y, nz.y, o.y )
        // ( nx.z, ny.z, nz.z, o.z )
        // (    0,    0,    0,   1 )
        // with nx, ny, nz being normalized window axis
        // and o being window origin (both in VR tracking coordinates)
        VRToWindowMatrix = new Matrix4x4();
        VRToWindowMatrix.SetRow(0, new Vector4(xAxis.x, xAxis.y, xAxis.z, -Vector3.Dot(xAxis, origin)));
        VRToWindowMatrix.SetRow(1, new Vector4(yAxis.x, yAxis.y, yAxis.z, -Vector3.Dot(yAxis, origin)));
        VRToWindowMatrix.SetRow(2, new Vector4(zAxis.x, zAxis.y, zAxis.z, -Vector3.Dot(zAxis, origin)));
        VRToWindowMatrix.SetRow(3, new Vector4(0, 0, 0, 1));

        Debug.Log("✅ Calibration complete");
        Debug.Log($"Width: {windowWidth:F3}  Height: {windowHeight:F3}");
        Debug.Log("VR → Window Matrix:\n" + VRToWindowMatrix);
    }
}
