using UnityEngine;
using UnityEngine.SceneManagement;

public class MazeExit : MonoBehaviour
{

    private void OnTriggerEnter(Collider other)
    {
            Debug.Log("You win!");
    }
}