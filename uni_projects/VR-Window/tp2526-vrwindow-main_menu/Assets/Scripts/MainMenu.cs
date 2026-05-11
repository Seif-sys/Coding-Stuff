using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{   
    public string nextSceneName = "Merge";
    public string windowSceneName = "Window";


    public void Play()
    {
            SceneManager.LoadScene(nextSceneName);
            SceneManager.LoadScene(windowSceneName, LoadSceneMode.Additive);

    }
    
}
