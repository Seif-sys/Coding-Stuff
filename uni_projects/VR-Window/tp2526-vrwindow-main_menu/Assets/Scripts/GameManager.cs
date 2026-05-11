using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    [Header("UI Panels")]
    public GameObject gameOverPanel;
    public GameObject winPanel;
    public GameObject musicLevel2;
    public GameObject musicLevel3;

    private bool isGameActive = true;
    public static GameManager instance;

    public int currentLevel = 1;
    public int keysCollected = 0;
    // Number of keys required to spawn the exit door
    public int keysToCollect = 3;
    private bool doorSpawned = false;

    public GridMazeGenerator mazeGenerator;
    public GameObject keyPrefab;
    public Transform interactablesParent;
    public GameObject monsterPrefab;
    public GameObject doorPrefab;

    void Awake()
    {
        instance = this;
    }

    void Start()
    {
        if (PlayerPrefs.HasKey("SavedLevel"))
        
            currentLevel = 1;//PlayerPrefs.GetInt("SavedLevel");
        
        // 1. Find the generator if missing
        if (mazeGenerator == null)
        {
            mazeGenerator = FindObjectOfType<GridMazeGenerator>();
        }

        if (mazeGenerator == null)
        {
            Debug.LogError("GameManager CANNOT find a MazeGenerator!");
            return;
        }

        // LoadCurrentLevel();

        // 2. CHECK WHICH LEVEL IS SELECTED
        LoadCurrentLevel();
    } 

    void Update()
    {
        int flag =0;
        if (keysCollected >= keysToCollect && !doorSpawned && mazeGenerator.exitWall != null)
        {
            // Spawn the door on first key collection
            if ((currentLevel == 2 || currentLevel == 3) && flag ==0)
            {
                SpawnExitDoor();
                doorSpawned = true;
                flag =1;
            }
        }

        if (!isGameActive)
        {
            // --- WIN SCENARIO ---
            if (winPanel != null && winPanel.activeSelf)
            {
                if (Input.GetKeyDown(KeyCode.R))
                {
                    SceneManager.UnloadSceneAsync("Level2");
                    SceneManager.LoadScene("Level2", LoadSceneMode.Additive);
                    // SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex, LoadSceneMode.Additive);
                }
            }
            // --- LOSE SCENARIO ---
            else if (gameOverPanel != null && gameOverPanel.activeSelf)
            {

                if (Input.GetKeyDown(KeyCode.R))
                {
                    SceneManager.UnloadSceneAsync("Level2");
                    SceneManager.LoadScene("Level2", LoadSceneMode.Additive);
                }
            }
            return;
        }

        if (isGameActive && keysCollected >= keysToCollect)
        {
            PlayerPrefs.SetInt("SavedLevel", 3); 
            PlayerPrefs.Save();                  
        }
    }

    // =============================
    // KEY SYSTEM
    // =============================
    public void AddKey()
    {
        keysCollected++;
        Debug.Log("Keys Collected: " + keysCollected);

        if (keysCollected >= keysToCollect)
        {
            if (currentLevel == 3)
            {
                Debug.Log("FINAL KEYS COLLECTED! Opening final exit...");
            }
        }
    }

    public void increaseLvl()
    {
        currentLevel++;
        if(currentLevel == 1) GoToLevel1();
        if(currentLevel == 2) GoToLevel2();
        if(currentLevel == 3) GoToLevel3();
        if(currentLevel > 3) WinGame();
    }
    // =============================
    // LEVEL 2
    // =============================
    
    // public void GoToLevel1()
    // {
    //     currentLevel = 1;
    //     doorSpawned = true;
    //     mazeGenerator.GenerateMaze();
    //     SpawnExitDoor();
    // }

    public void GoToLevel2()
    {
        currentLevel = 2;
        keysCollected = 0;
        RenderSettings.ambientIntensity = .2f;
        doorSpawned = false;
        if (musicLevel2 != null) musicLevel2.SetActive(true);
        if (musicLevel3 != null) musicLevel3.SetActive(false);
        mazeGenerator.GenerateMaze();
        SpawnKeys(keysToCollect);
        HideExistingDoors();
    }


    // LEVEL 3

    public void GoToLevel3()
    {
        currentLevel = 3;
        keysCollected = 0;
        doorSpawned = false;
        RenderSettings.ambientIntensity = .2f;

        if (musicLevel2 != null) musicLevel2.SetActive(false);
        if (musicLevel3 != null) musicLevel3.SetActive(true);
        mazeGenerator.GenerateMaze();
        SpawnKeys(keysToCollect);
        
        // Hide any existing doors before spawning new ones
        HideExistingDoors();
        
        SpawnMonster();
    }

    // FINAL EXIT - No longer needed, Update() handles door spawning
    // void UnlockFinalExit()
    // {
    //     if (mazeGenerator.exitWall != null)
    //     {
    //         SpawnExitDoor();
    //     }
    // }

    void SpawnExitDoor()
    {
        if (doorPrefab != null && mazeGenerator.exitWall != null)
        {
            Vector3 doorPos = mazeGenerator.exitWall.transform.position;
            GameObject door = Instantiate(doorPrefab, doorPos, Quaternion.identity);
            
            // Apply custom position offset, rotation, and scale
            door.transform.localPosition += new Vector3(0.5f, 0f, -0.22f);
            door.transform.rotation = Quaternion.Euler(0, 95, 0);
            door.transform.localScale = new Vector3(5f, 5f, 5f);
            
            // Add MazeExit component if door doesn't have it
            MazeExit_N mazeExit = door.GetComponent<MazeExit_N>();
            if (mazeExit == null)
            {
                mazeExit = door.AddComponent<MazeExit_N>();
            }
            
            // Activate the door so it becomes a trigger and listens for player
            mazeExit.Activate();
            
            // Make the original wall trigger so it doesn't block the door
            Collider wallCollider = mazeGenerator.exitWall.GetComponent<Collider>();
            if (wallCollider != null)
            {
                wallCollider.isTrigger = true;
            }
            
            mazeGenerator.exitWall.SetActive(false); // Hide the original wall
            
            Debug.Log("Door spawned after collecting " + keysCollected + " keys!");
        }
        else
        {
            Debug.LogWarning("Door prefab or exit wall not assigned!");
        }
    }

    void HideExistingDoors()
    {
        // Find and deactivate any existing doors
        MazeExit_N[] existingDoors = FindObjectsOfType<MazeExit_N>();
        foreach (MazeExit_N door in existingDoors)
        {
            door.gameObject.SetActive(false);
        }
    }




    // MONSTER SPAWN

    void SpawnMonster()
    {
        if (monsterPrefab != null)
        {
            Vector3 spawnPos = mazeGenerator.transform.position + new Vector3(0, 0, 0);
            GameObject monster = Instantiate(monsterPrefab, spawnPos, Quaternion.identity);
            monster.GetComponent<GridMonster>().gameOverUI = GameObject.Find("GameOverPanel");
        }
    }

    // KEY SPAWN

    void SpawnKeys(int amount)
    {
        for (int i = 0; i < amount; i++)
        {
            int rx = Random.Range(0, mazeGenerator.width);
            int ry = Random.Range(0, mazeGenerator.height);

            Vector3 pos = mazeGenerator.transform.position +
                          new Vector3(
                              (rx * mazeGenerator.cellSize),
                              1f,
                              (ry * mazeGenerator.cellSize)
                          );

            Instantiate(keyPrefab, pos, Quaternion.identity, interactablesParent);
        }
    }

    public void GameOver()
    {
        Debug.Log("Game Over!");
        isGameActive = false;
        Time.timeScale = 0f;

        if (gameOverPanel != null) gameOverPanel.SetActive(true);
    }

    public void WinGame()
    {
        Debug.Log("You Won!");
        isGameActive = false;
        Time.timeScale = 0f;

        if (winPanel != null) winPanel.SetActive(true);
    }

public void GoToLevel1()
{
    currentLevel = 1;
    keysCollected = 0;
    doorSpawned = true;

    // Music & UI
    if (musicLevel2 != null) musicLevel2.SetActive(false);
    if (musicLevel3 != null) musicLevel3.SetActive(false);

    // Generate maze
    mazeGenerator.GenerateMaze();
    SpawnExitDoor();
    RenderSettings.ambientIntensity = .7f;
    // Spawn keys if needed
   // SpawnKeys(keysToCollect);

    // No monsters for Level 1
}
    void LoadCurrentLevel()
    {
        Time.timeScale = 1f;
       // SceneManager.LoadScene("Level2", LoadSceneMode.Single);
        // SceneManager.LoadScene("Window", LoadSceneMode.Additive);
        switch (currentLevel)
        {
             case 1: GoToLevel1();
                     break;
            case 2: GoToLevel2();
                    break;
            case 3: GoToLevel3();
                    break;

        }
            
    }

    // void RestartGame()
    // {
    //     Time.timeScale = 1f;
    //     SceneManager.LoadScene("Merge", LoadSceneMode.Single);
    //     SceneManager.LoadScene("Window", LoadSceneMode.Additive);

    // }

    void LoadMergeScene()
    {
        PlayerPrefs.SetInt("SavedLevel", 2);
        Time.timeScale = 1f;
        SceneManager.LoadScene("Merge", LoadSceneMode.Single);
        SceneManager.LoadScene("Window", LoadSceneMode.Additive);
    }
}
