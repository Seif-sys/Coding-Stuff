using UnityEngine;

public class MazeExit_N : MonoBehaviour
{
    private Renderer rend;
    private bool activated = false;

    void Start()
    {
        rend = GetComponent<Renderer>();
    }

    public void Activate()
    {
        if (!activated)
        {
            activated = true;

            Collider col = GetComponent<Collider>();
            if (col != null)
            {
                col.isTrigger = true;
            }
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!activated)
            return;

        if (other.CompareTag("Player"))
        {
            GameManager.instance.increaseLvl();
        }
    }
}
