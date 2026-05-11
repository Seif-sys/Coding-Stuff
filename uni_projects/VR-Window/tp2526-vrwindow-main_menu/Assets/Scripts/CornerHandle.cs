using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class CornerHandle : MonoBehaviour, IDragHandler
{
    bool visible = true;
    Image img;
    public System.Action OnDragged;
    RectTransform rt;

    void Start()
    {
        img = GetComponent<Image>();
    }
    
    void Awake()
    {
        rt = GetComponent<RectTransform>();
    }

    public void OnDrag(PointerEventData eventData)
    {
        Vector2 pos;
        RectTransformUtility.ScreenPointToLocalPointInRectangle(
            rt.parent as RectTransform,
            eventData.position,
            eventData.pressEventCamera,
            out pos);

        rt.anchoredPosition = pos;
        OnDragged?.Invoke();
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            visible = !visible;
            Color c = img.color;
            c.a = visible ? 1f : 0;
            img.color = c;
        }
    }
}
