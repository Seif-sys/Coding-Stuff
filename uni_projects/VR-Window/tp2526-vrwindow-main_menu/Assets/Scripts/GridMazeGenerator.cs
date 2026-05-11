using System.Collections.Generic;
using UnityEngine;

public class GridMazeGenerator : MonoBehaviour
{
    [Header("Materials")]
    public Material floorMaterial;
    public Material wallMaterial;

    [Header("Maze Size")]
    public int width = 15;
    public int height = 15;

    [Header("Build Settings")]
    public float cellSize = 2f;
    public float wallHeight = 2.5f;
    public float wallThickness = 0.2f;

    [Header("Seed")]
    public bool randomSeed = true;//test
    public int seed = 0;


    // EXIT SYSTEM
    public GameObject exitWall;
    private bool exitAssigned = false;

    [ContextMenu("Generate Maze")]


    public void GenerateMaze()
    {
        // Clear previous
        for (int i = transform.childCount - 1; i >= 0; i--)
            Destroy(transform.GetChild(i).gameObject);

        exitAssigned = false;
        exitWall = null;

        int usedSeed = randomSeed ? Random.Range(int.MinValue, int.MaxValue) : seed;
        var rng = new System.Random(usedSeed);

        // walls[x,y,dir] dir: 0=N,1=E,2=S,3=W
        bool[,,] walls = new bool[width, height, 4];
        bool[,] visited = new bool[width, height];

        for (int x = 0; x < width; x++)
            for (int y = 0; y < height; y++)
                for (int d = 0; d < 4; d++)
                    walls[x, y, d] = true;

        Stack<(int x, int y)> stack = new();
        int cx = 0, cy = 0;
        visited[cx, cy] = true;
        stack.Push((cx, cy));

        int[] dx = { 0, 1, 0, -1 };
        int[] dy = { 1, 0, -1, 0 };

        while (stack.Count > 0)
        {
            (cx, cy) = stack.Peek();

            List<int> neighbors = new();
            for (int d = 0; d < 4; d++)
            {
                int nx = cx + dx[d];
                int ny = cy + dy[d];
                if (nx >= 0 && nx < width && ny >= 0 && ny < height && !visited[nx, ny])
                    neighbors.Add(d);
            }

            if (neighbors.Count == 0)
            {
                stack.Pop();
                continue;
            }

            int dir = neighbors[rng.Next(neighbors.Count)];
            //int dir = neighbors[0];//test

            int tx = cx + dx[dir];
            int ty = cy + dy[dir];

            walls[cx, cy, dir] = false;
            walls[tx, ty, (dir + 2) % 4] = false;

            visited[tx, ty] = true;
            stack.Push((tx, ty));
        }
        walls[width - 1, height - 1, 0] = true;  
        walls[width - 1, height - 1, 2] = false; 
        walls[width - 1, height - 1, 3] = false; 
        BuildFloor();
        BuildWalls(walls);

    }

    void BuildFloor()
    {
        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.SetParent(transform, false);

        float sizeX = width * cellSize / 10f;
        float sizeZ = height * cellSize / 10f;
        floor.transform.localScale = new Vector3(sizeX, 1f, sizeZ);

        floor.transform.localPosition =
            new Vector3((width - 1) * cellSize * 0.5f, 0f, (height - 1) * cellSize * 0.5f);

        if (floorMaterial != null)
            floor.GetComponent<Renderer>().material = floorMaterial;
    }

   void BuildWalls(bool[,,] walls)
{
    int side = Random.Range(0, 4); // 0=N, 1=E, 2=S, 3=W
    int randomIndex = Random.Range(0, width);

    for (int x = 0; x < width; x++)
    {
        for (int y = 0; y < height; y++)
        {
            Vector3 cellCenter = new Vector3(x * cellSize, wallHeight * 0.5f, y * cellSize);

            // NORTH
            if (walls[x, y, 0])
            {
                GameObject w = CreateWall(cellCenter + new Vector3(0, 0, cellSize * 0.5f), true);

                    if (x == width - 1 && y == height - 1)
                    {
                        exitWall = w;
                        w.name = "ExitDoor";       
                        w.AddComponent<MazeExit>(); 
                    }
                }

            // EAST
            if (walls[x, y, 1])
            {
                GameObject w = CreateWall(cellCenter + new Vector3(cellSize * 0.5f, 0, 0), false);

                if (side == 1 && x == width - 1 && y == randomIndex && !exitAssigned)
                {
                    exitWall = w;
                    exitAssigned = true;
                    w.AddComponent<MazeExit>();
                }
            }

            // SOUTH boundary
            if (y == 0)
            {
                GameObject w = CreateWall(cellCenter + new Vector3(0, 0, -cellSize * 0.5f), true);

                if (side == 2 && x == randomIndex && !exitAssigned)
                {
                    exitWall = w;
                    exitAssigned = true;
                    w.AddComponent<MazeExit>();
                }
            }

            // WEST boundary
            if (x == 0)
            {
                GameObject w = CreateWall(cellCenter + new Vector3(-cellSize * 0.5f, 0, 0), false);

                if (side == 3 && y == randomIndex && !exitAssigned)
                {
                    exitWall = w;
                    exitAssigned = true;
                    w.AddComponent<MazeExit>();
                }
            }
        }
    }

    if (exitWall != null)
        Debug.Log("Exit Wall created on side: " + side);
    else
        Debug.Log("Exit Wall NOT created!");
}

    GameObject CreateWall(Vector3 pos, bool horizontal)
    {
        GameObject wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.name = "Wall";
        wall.transform.SetParent(transform, false);

        float length = cellSize + wallThickness;
        wall.transform.localScale = horizontal
            ? new Vector3(length, wallHeight, wallThickness)
            : new Vector3(wallThickness, wallHeight, length);

        wall.transform.localPosition = pos;

        if (wallMaterial != null)
            wall.GetComponent<Renderer>().material = wallMaterial;
        //
        wall.layer = LayerMask.NameToLayer("Walls");

        return wall;
    }
}
