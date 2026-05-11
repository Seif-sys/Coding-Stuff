using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class SimplePawnController : MonoBehaviour
{
    public float moveSpeed = 5.5f;
    public float lookSpeed = 60f;
    public Transform cameraTransform;

    private CharacterController cc;
    private float verticalLookRotation = 0f;

    void Awake()
    {
        cc = GetComponent<CharacterController>();
        if (cameraTransform == null) cameraTransform = GetComponentInChildren<Camera>().transform;
    }

    void Update()
    {
        // 1. DIRECTIONAL MOVEMENT (Forward, Back, Left, Right)
        // Up Arrow/W = 1, Down Arrow/S = -1
        float vertical = Input.GetAxis("Vertical");
        // Right Arrow/D = 1, Left Arrow/A = -1
        float horizontal = Input.GetAxis("Horizontal");

        // Calculate movement based on where the player is facing
        Vector3 move = (transform.forward * vertical) + (transform.right * horizontal);

        // Move the Character Controller
        cc.SimpleMove(move * moveSpeed);

        // 2. CAMERA LOOK (U and Z)
        if (Input.GetKey(KeyCode.U)) verticalLookRotation -= lookSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.Z)) verticalLookRotation += lookSpeed * Time.deltaTime;

        // Clamp to prevent flipping
        verticalLookRotation = Mathf.Clamp(verticalLookRotation, -80f, 80f);
        cameraTransform.localRotation = Quaternion.Euler(verticalLookRotation, 0, 0);
    }
}
