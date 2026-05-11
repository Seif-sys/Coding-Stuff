using UnityEngine;

public class Key : MonoBehaviour
{
    private AudioSource audioSource;

    private void Start()
    {
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            Debug.LogWarning("Key: No AudioSource found on this key!");
        }
        else if (audioSource.clip == null)
        {
            Debug.LogWarning("Key: AudioSource has no clip assigned!");
        }
        else
        {
            Debug.Log("Key: AudioSource detected with clip: " + audioSource.clip.name);
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player"))
            return;

        GameManager.instance.AddKey();

        // Play the sound at position (so it still plays after we destroy the key)
        if (audioSource != null && audioSource.clip != null)
        {
            AudioSource.PlayClipAtPoint(audioSource.clip, transform.position);
        }

        // Destroy the key immediately so it doesn't linger as a trigger
        Destroy(gameObject);
    }
}
