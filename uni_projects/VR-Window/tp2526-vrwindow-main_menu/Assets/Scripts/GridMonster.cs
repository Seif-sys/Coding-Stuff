using UnityEngine;
using System.Collections.Generic;
using UnityEngine.SceneManagement;

public class GridMonster : MonoBehaviour
{
    public Transform player;
    public GameObject gameOverUI;
    public float moveSpeed = 2.0f;

    public float gridSize = 2.0f;
    public LayerMask wallLayer;
    private Vector3 targetGridPos;
    private bool isMoving = false;
    private Dictionary<Vector2Int, int> tileVisits = new Dictionary<Vector2Int, int>();

    void Start()
    {
        if (player == null)
            player = GameObject.FindGameObjectWithTag("Player")?.transform;
        targetGridPos = GetNearestGridPos(transform.position);
        transform.position = targetGridPos;
        RegisterVisit(targetGridPos);
    }

    void Update()
    {
        if (player == null) return;

        float distance = Vector3.Distance(
            new Vector3(transform.position.x, 0, transform.position.z),
            new Vector3(player.position.x, 0, player.position.z)
        );

        if (Vector3.Distance(transform.position, player.position) < 0.5f)
        {
            CatchPlayer();
        }

        if (isMoving)
        {
            MoveToTarget();
        }
        else
        {
            PickBestTile();
        }
    }

    void MoveToTarget()
    {
        transform.position = Vector3.MoveTowards(transform.position, targetGridPos, moveSpeed * Time.deltaTime);

        Vector3 dir = (targetGridPos - transform.position).normalized;
        if (dir != Vector3.zero)
        {
            Quaternion toRotation = Quaternion.LookRotation(dir);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, toRotation, 720 * Time.deltaTime);
        }

        if (Vector3.Distance(transform.position, targetGridPos) < 0.05f)
        {
            transform.position = targetGridPos;
            isMoving = false;
            RegisterVisit(targetGridPos);
        }
    }

    void OnTriggerEnter(Collider other)
{
    // Check if the object that collided has the "Player" tag
    if (other.CompareTag("Player"))
    {
        CatchPlayer();
    }
}

    void PickBestTile()
    {
        Vector3[] directions = { Vector3.forward, Vector3.back, Vector3.left, Vector3.right };
        Vector3 bestMove = transform.position;
        float bestScore = -9999f;
        bool foundMove = false;

        foreach (Vector3 dir in directions)
        {
            Vector3 potentialPos = transform.position + (dir * gridSize);

            if (Physics.Linecast(transform.position, potentialPos, wallLayer)) continue;

            int visits = GetVisitCount(potentialPos);
            float distToPlayer = Vector3.Distance(potentialPos, player.position);

            float score = -(visits * 10.0f) - distToPlayer;
            if (Vector3.Dot(dir, transform.forward) < -0.9f) score -= 1.0f;

            if (score > bestScore)
            {
                bestScore = score;
                bestMove = potentialPos;
                foundMove = true;
            }
        }

        if (foundMove)
        {
            targetGridPos = bestMove;
            isMoving = true;
        }
    }

    void RegisterVisit(Vector3 pos)
    {
        Vector2Int key = GetGridKey(pos);
        if (tileVisits.ContainsKey(key)) tileVisits[key]++;
        else tileVisits[key] = 1;
    }

    int GetVisitCount(Vector3 pos)
    {
        Vector2Int key = GetGridKey(pos);
        return tileVisits.ContainsKey(key) ? tileVisits[key] : 0;
    }

    void CatchPlayer()
{
    GetComponent<AudioSource>()?.Play();

    GameManager manager = FindObjectOfType<GameManager>();
    if (manager != null)
    {
        manager.GameOver();
    }

    enabled = false;
}

    Vector2Int GetGridKey(Vector3 pos)
    {
        return new Vector2Int(Mathf.RoundToInt(pos.x), Mathf.RoundToInt(pos.z));
    }

    Vector3 GetNearestGridPos(Vector3 pos)
    {
        float x = Mathf.Round(pos.x / gridSize) * gridSize;
        float z = Mathf.Round(pos.z / gridSize) * gridSize;
        return new Vector3(x, pos.y, z);
    }
}