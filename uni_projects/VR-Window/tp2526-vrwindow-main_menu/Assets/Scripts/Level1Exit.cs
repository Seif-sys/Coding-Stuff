
using UnityEngine;
using UnityEngine.SceneManagement;

public class Level1Exit : MonoBehaviour
{
    public string nextSceneName = "Level2";
    public string windowSceneName = "Window";

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            //GameManager.instance.increaseLvl();
            SceneManager.LoadScene(nextSceneName, LoadSceneMode.Additive);
            SceneManager.LoadScene(windowSceneName, LoadSceneMode.Additive);
            SceneManager.UnloadSceneAsync("Merge");
        }
    }
}
