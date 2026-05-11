using UnityEngine;

public class MusicSwitch : MonoBehaviour
{
    public GameObject musicLevel2;
    public GameObject musicLevel3;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player")) return;

        if (musicLevel2 != null) musicLevel2.SetActive(false);
        if (musicLevel3 != null) musicLevel3.SetActive(true);

        Destroy(gameObject);
    }

}
