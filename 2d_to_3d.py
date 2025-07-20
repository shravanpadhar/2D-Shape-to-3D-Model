import cv2
import numpy as np
import multiprocessing
import cadquery as cq
import trimesh
import time
import math
from trimesh.transformations import rotation_matrix

# Custom SceneViewer to position the Trimesh window
from trimesh.viewer.windowed import SceneViewer
from pyglet.canvas import Display

class PositionedSceneViewer(SceneViewer):
    def __init__(self, *args, **kwargs):
        self.position = kwargs.pop('position', (700, 100))
        self.resolution = kwargs.get('resolution', (800, 800))
        display = Display()
        screen = display.get_default_screen()
        self.screen_width = screen.width
        self.screen_height = screen.height
        self.positioned = False
        super(PositionedSceneViewer, self).__init__(*args, **kwargs)

    def dispatch_event(self, *args):
        if not self.positioned:
            # Set the location of the window
            x, y = self.position
            self.set_location(x, y)
            self.positioned = True
        return super(PositionedSceneViewer, self).dispatch_event(*args)

def get_all_contours(frame, min_area=1000):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    _, mask = cv2.threshold(edges, 80, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    for cnt in contours:
        if cv2.contourArea(cnt) >= min_area:
            eps = 0.02 * cv2.arcLength(cnt, True)
            poly = cv2.approxPolyDP(cnt, eps, True)
            polygons.append(poly.reshape(-1, 2))
    return polygons

def build_and_export_multiple(polygons, thickness_cm=10):
    scale = 0.1  # 1 pixel ≈ 0.1cm
    solids = []
    for pts in polygons:
        pts_scaled = [(x * scale, y * scale) for x, y in pts]
        wp = cq.Workplane("XY").polyline(pts_scaled).close()
        solid = wp.extrude(thickness_cm)
        solids.append(solid)
    if not solids:
        print("[!] No valid shapes to export.")
        return
    combined = solids[0]
    for solid in solids[1:]:
        combined = combined.union(solid)
    combined.val().exportStl("live_model.stl")
    print("[+] Exported STL with multiple shapes (height ≈10 cm)")

def preview_thread_fn():
    try:
        mesh = trimesh.load("live_model.stl", force="mesh")
        scene = trimesh.Scene(mesh)
        scene.background = [255, 255, 255, 255]
        scene.rezero()
        center = mesh.bounding_box.centroid
        bbox = mesh.bounding_box.extents
        max_dim = np.max(bbox)
        fit_distance = max_dim * 2.0
        scene.set_camera(angles=[math.radians(45), 0, 0], distance=fit_distance, center=center)
        def rot_cb(scene_inner):
            angle = (time.time() * 60) % 360  # 360° in 6s
            R = rotation_matrix(np.deg2rad(angle), [0, 0, 1], center)
            node = list(scene_inner.graph.nodes_geometry)[0]
            scene_inner.graph.update(node, matrix=R)
        # Use the custom viewer to set window position
        scene.show(
            viewer=PositionedSceneViewer,
            callback=rot_cb,
            smooth=True,
            resolution=(800, 800),
            position=(700, 100)  # Move window to (700, 100)
        )
    except Exception as e:
        print(f"Preview error: {e}")

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Cannot open webcam")
        return

    preview_process = None
    print("Press 's' to snapshot & spin 3D model")
    print("Press 'q' in the webcam window to quit")

    window_name = "Live Sketch | Press 's' to spin 3D"

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        disp = frame.copy()
        polygons = get_all_contours(frame)
        for poly in polygons:
            cv2.drawContours(disp, [poly], -1, (0, 255, 0), 2)
        cv2.imshow(window_name, disp)
        cv2.moveWindow(window_name, 0, 0)  # Ensure webcam window is at top-left

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and polygons:
            build_and_export_multiple(polygons)
            if preview_process and preview_process.is_alive():
                preview_process.terminate()
                preview_process.join(timeout=1)
            preview_process = multiprocessing.Process(
                target=preview_thread_fn
            )
            preview_process.daemon = True
            preview_process.start()
        elif key == ord('q'):
            break

    if preview_process and preview_process.is_alive():
        preview_process.terminate()
    cap.release()
    cv2.destroyAllWindows()
    print("[*] Bye!")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')  # For Windows compatibility
    main()
