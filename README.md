# 2D-Shape-to-3D-Model
Convert real-time 2D sketches from your webcam into dynamic, rotatable 3D models using only Python! This project uses OpenCV, CadQuery, and Trimesh to extract contours, extrude them into 3D, and preview the final model with a rotating animation
---

##  Working 

- Captures shapes drawn live in front of your webcam.
- Detects external contours using image processing.
- Converts the 2D shapes into **3D extruded models**.
- Automatically exports the 3D object as an **STL file**.
- Opens a real-time rotatable 3D model viewer for preview.

---

##  Features

- Real-time shape detection  
- Multiple shape extrusion  
- Automatic STL export  
- Live 3D model rotation preview  
- Fully Python-based (No Blender or external modeling tools!)

---

##  Requirements

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/)
- [CadQuery](https://github.com/CadQuery/cadquery)
- [Trimesh](https://trimsh.org/)
- [Pyglet](https://pyglet.readthedocs.io/)

###  Install dependencies:

```bash
pip install opencv-python cadquery trimesh pyglet numpy

### How to Run

```bash
python 2d_to_3d.py


##  Author

**Shravan Kailas Padhar**  
📫 [LinkedIn](https://www.linkedin.com/in/shravan) • [Twitter](https://twitter.com/your_twitter_handle)
