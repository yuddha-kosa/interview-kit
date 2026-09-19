In quad tree..the world is divided into quadrants and each quadrant is subdivided once it crosses the threshold...each quadrant will have coordinates...associated with them...when a restaurant needs to be onboarded...their coordinate will be compared to the quadrant and see where it fits and accordingly it will be kept at the right place after tree traversal...
if we need to search then the search coordinate + circle distance..whatever quadrant comes in ..we will search those quadrants and give the result ?
## Architectural Note: The Quadtree Engine & Geospatial Lifecycle
A Quadtree is a dynamic, hierarchical tree data structure used to spatial-partition a two-dimensional space. Unlike fixed, uniform grids (such as Geohashing), a Quadtree dynamically scales its layout size and branch depth in memory based entirely on local data density.
------------------------------
## 1. Core Structure & Coordinate Definitions
Every element (node) in a Quadtree represents a distinct Bounding Box defined explicitly by four floating-point variables:

* Longitude boundaries: x_min, x_max
* Latitude boundaries: y_min, y_max

An internal parent node always maintains exactly four child pointers representing the four geographic quadrants split precisely down its horizontal and vertical center lines:

   1. NW (North-West)
   2. NE (North-East)
   3. SW (South-West)
   4. SE (South-East)

------------------------------
## 2. Onboarding Workflow: The Dynamic Splitting Example## The System Rule
You roll out a brand-new DoorDash region. To optimize performance, you configure a node capacity constraint: A single leaf node can hold a maximum of 2 restaurants. If a 3rd item enters a box, it must subdivide.
## Step 1: Initial State (Sparse Suburbs)
You register your first two restaurants in a spacious country valley:

* A&W Burgers
* Taco Casa

The database maps them both directly into the primary top-level box (The Root). Because the item count is within limits (2 ≤ 2), no partitioning occurs.

+---------------------------------------+

|                                       |
|   • A&W Burgers                       |
|                                       |
|                         • Taco Casa   |
|                                       |
+---------------------------------------+

## Step 2: The Splitting Trigger (High-Density Onboarding)
You expand onboarding into a crowded downtown core. Three new restaurants register:

* Downtown Sushi
* Capital Pizza
* Texas BBQ

The root box now contains 5 total items (5 > 2), which violates the capacity constraint.
The system instantly reads the root midpoints (mid_lon and mid_lat), instantiates 4 smaller child quadrants, and re-allocates the restaurants into their respective coordinate boxes:

+-------------------+-------------------+

|                   |                   |
|        NW         |   • A&W Burgers   |
|                   |        NE         |
+-------------------+-------------------+

|  • Downtown Sushi |                   |
|  • Capital Pizza  |    • Taco Casa    |
|  • Texas BBQ (SW) |        SE         |
+-------------------+-------------------+

## Step 3: Deep Hierarchical Partitioning
The South-West (SW) quadrant (Downtown) now holds 3 items, still violating the capacity limit.
The tree isolates only the SW box, computes its smaller local midpoints, and subdivides it into four granular sub-quadrants (SW-NW, SW-NE, SW-SW, SW-SE). The sparse suburbs (NW, NE, SE) remain entirely untouched.

+-------------------+-------------------+

|                   |                   |
|        NW         |   • A&W Burgers   |
|                   |        NE         |
+---------+---------+-------------------+

|  •Sushi |         |                   |
|  SW-NW  |  SW-NE  |                   |
+---------+---------+    • Taco Casa    |

| •Pizza  |  •BBQ   |        SE         |
|  SW-SW  |  SW-SE  |                   |
+---------+---------+-------------------+

------------------------------
## 3. Search Workflow: Solving the Boundary Condition
A user stands directly on a boundary line downtown. Their left foot is in the SW-SW box, but they are right on the edge of the SW-SE box. They search for restaurants within a 5 km delivery radius.
## Step 1: Generating the Query Window
The backend transforms the user's raw GPS point and 5 km radius into a spatial Search Window (a mathematical circle or query box).
## Step 2: Multi-Path Tree Traversal (Tree Pruning)
The algorithm starts at the Root and evaluates the Search Window against the quadrant boundaries using an overlap check:

* Pruning: The window does not intersect with the northern hemisphere. The system instantly discards the entire NW and NE branches, dropping thousands of distant records in a single instruction cycle.
* Multi-Path Selection: Because the user is right on a border, the 5 km search circle overlaps both the SW and SE regions. The tree traversal does not fail or reset; it opens both primary root branches simultaneously to track down both sides of the boundary line.

                  [ GLOBAL ROOT ]
                     /       \
          [SW Branch]         [SE Branch]
            /  |  \  \          /  |  \  \
           O   O   O   X       X   O   O   O

                       |       |
                 (Downtown)  (Downtown)

As the algorithm goes deeper, it uses smaller local midpoints to prune aggressively, instantly narrowing down to just 2 tiny leaf blocks (SW-SW and SW-SE) instead of scanning the entire map.
## Step 3: Candidate Extraction & Exact Vector Sorting
The tree returns the small group of raw coordinate candidates residing in those specific leaf buckets:

* Capital Pizza (SW-SW): Extracted.
* Texas BBQ (SW-SE): Extracted.
* Suburban Restaurant (200 miles away in SE root leaf): Extracted (because that sparse suburban bucket hasn't split into smaller boxes yet).

The backend hands this small candidate list over to the application layer to perform Exact Distance Filtering. It calculates the true straight-line distance from the user's exact coordinate using the Haversine Formula:

import math
def calculate_exact_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
# 1. Capital Pizza: 0.005 km -> (0.005 <= 5km) -> VALID (Ranked #1)# 2. Suburban Shop: 321.0 km -> (321.0  > 5km) -> INVALID (Discarded)

The system filters out the distant suburban restaurant that was pulled by the un-split box, sorts the valid downtown results by true proximity, and renders them onto the user's UI.
Would you like to complement these design notes with the complete Python source code for inserting points and managing splits inside a Quadtree object, or move on to how Uber's H3 Hexagons solve the corner-to-side distance distortion?

