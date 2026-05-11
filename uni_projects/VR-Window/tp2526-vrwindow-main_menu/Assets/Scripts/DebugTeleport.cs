using UnityEngine;

public class DebugTeleport : MonoBehaviour
{
    public Transform playerRoot;
    private int keyIndex = 0;

    void Start()
    {
        if (playerRoot == null)
            playerRoot = GameObject.FindGameObjectWithTag("Player").transform;
    }

    void Update()
    {
        // Press K to go to Key
        if (Input.GetKeyDown(KeyCode.K)) TeleportToNextKey();

        // Press E to go to Exit
        if (Input.GetKeyDown(KeyCode.E)) TeleportToExit();
    }

    void TeleportToNextKey()
    {
        // 1. SAFE CHECK: Find the Interactables parent
        Transform keyParent = GameManager.instance.interactablesParent;

        // Auto-fix if you forgot to assign it in Inspector
        if (keyParent == null)
        {
            GameObject foundObj = GameObject.Find("Interactables");
            if (foundObj != null) keyParent = foundObj.transform;
        }

        if (keyParent == null || keyParent.childCount == 0)
        {
            Debug.LogError("Still cannot find any Keys! Did you assign 'Interactables Parent' in GameManager?");
            return;
        }

        // 2. Cycle through keys
        if (keyIndex >= keyParent.childCount) keyIndex = 0;
        Transform targetKey = keyParent.GetChild(keyIndex);

        // 3. Teleport with OFFSET (0.7m away on X axis)
        // This puts you next to the key, not inside it.
        Vector3 safePos = targetKey.position + new Vector3(0.7f, 0, 0);

        MovePlayer(safePos);

        Debug.Log("Jumped to Key " + (keyIndex + 1));
        keyIndex++;
    }

    void TeleportToExit()
    {
        // 1. Check if exit exists
        if (GameManager.instance.mazeGenerator == null) return;
        GameObject exit = GameManager.instance.mazeGenerator.exitWall;

        if (exit == null)
        {
            Debug.Log("Exit wall not built yet!");
            return;
        }

        // 2. Calculate the Center of the Maze
        // We use this to find which way is "Backwards" from the door
        GridMazeGenerator gen = GameManager.instance.mazeGenerator;
        float midX = gen.width * gen.cellSize / 2f;
        float midZ = gen.height * gen.cellSize / 2f;
        Vector3 mazeCenter = new Vector3(midX, 0, midZ);

        // 3. Find direction FROM Exit TO Center
        Vector3 directionToCenter = (mazeCenter - exit.transform.position).normalized;

        // 4. Move 3 meters away from the door towards the center
        // This guarantees you stand in the room BEFORE the exit.
        Vector3 safePos = exit.transform.position + (directionToCenter * 3.0f);

        // Ensure we are standing on the floor (Y = 1)
        safePos.y = 1f;

        MovePlayer(safePos);
        Debug.Log("Jumped safely in FRONT of Exit!");
    }

    // Helper to move player safely
    void MovePlayer(Vector3 target)
    {
        CharacterController cc = playerRoot.GetComponent<CharacterController>();
        if (cc) cc.enabled = false; // Disable physics

        playerRoot.position = target;

        if (cc) cc.enabled = true;  // Re-enable physics
    }
}