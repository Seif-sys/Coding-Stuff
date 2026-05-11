using UnityEngine;
using System.Collections;

public class ObserverInfluence : MonoBehaviour
{
    public Transform player;

    public float idleTimeToTrigger = 15f;
    public float wallDuration = 40f;

    private Vector3 lastPosition;
    private float idleTimer = 0f;
    private GameObject activeWall = null;

    void Start()
    {
        lastPosition = player.position;
    }

    void Update()
    {
        float movedDistance = Vector3.Distance(player.position, lastPosition);

        if (movedDistance < 0.01f)
        {
            idleTimer += Time.deltaTime;
        }
        else
        {
            idleTimer = 0f;
        }

        if (idleTimer >= idleTimeToTrigger && activeWall == null)
        {
            SpawnWallInFront();
            idleTimer = 0f;
        }

        lastPosition = player.position;
    }

    void SpawnWallInFront()
    {
        Vector3 spawnPos = player.position + player.forward * 2f;
        spawnPos.y = 1.25f;

        activeWall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        activeWall.transform.position = spawnPos;
        activeWall.transform.localScale = new Vector3(2f, 2.5f, 0.3f);

        StartCoroutine(RemoveWallAfterTime());
    }

    IEnumerator RemoveWallAfterTime()
    {
        yield return new WaitForSeconds(wallDuration);

        if (activeWall != null)
            Destroy(activeWall);

        activeWall = null;
    }
}
