import pathlib

import numpy
from numpy.linalg import norm
from PIL import Image


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH_TO_OBJ_FILE = REPO_ROOT / "assets/2026_05_20_three_dimension_idea/cube_test.obj"
PATH_TO_OUTPUT_IMAGE = (
    REPO_ROOT / "assets/2026_05_26_three_dimension_output_and_cost/cube_render.png"
)
WORLD_UP_VECTOR = numpy.array([0.0, 1.0, 0.0])


def parse_obj_file(path_to_obj_file: pathlib.Path):
    vertices = []
    faces = []

    with path_to_obj_file.open() as obj_file:
        for line in obj_file:
            parts = line.split()

            if not parts:
                continue

            if parts[0] == "v":
                vertices.append([float(value) for value in parts[1:4]])

            if parts[0] == "f":
                face = []

                for vertex_reference in parts[1:]:
                    vertex_index = int(vertex_reference.split("/")[0])
                    face.append(vertex_index - 1)

                faces.append(face)

    return numpy.array(vertices), faces


def centroid(coordinates: numpy.ndarray) -> numpy.ndarray:
    return numpy.mean(coordinates, axis=0)


def normalize(vector: numpy.ndarray) -> numpy.ndarray:
    return vector / norm(vector)


def project_vertices(
    vertices: numpy.ndarray,
    camera_position: numpy.ndarray,
    target: numpy.ndarray,
    frame_width: int,
    frame_height: int,
):
    forward_vector = normalize(target - camera_position)
    right_vector = normalize(numpy.cross(forward_vector, WORLD_UP_VECTOR))
    true_up_vector = numpy.cross(right_vector, forward_vector)

    relative_vertices = vertices - camera_position
    x_camera = relative_vertices @ right_vector
    y_camera = relative_vertices @ true_up_vector
    z_camera = relative_vertices @ forward_vector

    focal_length = min(frame_width, frame_height) * 0.8

    x_pixel = frame_width / 2 + focal_length * (x_camera / z_camera)
    y_pixel = frame_height / 2 - focal_length * (y_camera / z_camera)

    screen_vertices = numpy.column_stack([x_pixel, y_pixel])

    return screen_vertices, z_camera


def barycentric_coordinates(point, a, b, c):
    denominator = (
        (b[1] - c[1]) * (a[0] - c[0])
        + (c[0] - b[0]) * (a[1] - c[1])
    )

    if abs(denominator) < 1e-12:
        return None

    alpha = (
        (b[1] - c[1]) * (point[0] - c[0])
        + (c[0] - b[0]) * (point[1] - c[1])
    ) / denominator
    beta = (
        (c[1] - a[1]) * (point[0] - c[0])
        + (a[0] - c[0]) * (point[1] - c[1])
    ) / denominator
    gamma = 1.0 - alpha - beta

    return alpha, beta, gamma


def pixels_inside_triangle(triangle_pixels, triangle_depths, frame_width, frame_height):
    a, b, c = triangle_pixels
    depth_a, depth_b, depth_c = triangle_depths

    min_x = max(0, int(numpy.floor(min(a[0], b[0], c[0]))))
    max_x = min(frame_width - 1, int(numpy.ceil(max(a[0], b[0], c[0]))))
    min_y = max(0, int(numpy.floor(min(a[1], b[1], c[1]))))
    max_y = min(frame_height - 1, int(numpy.ceil(max(a[1], b[1], c[1]))))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            pixel_center = numpy.array([x + 0.5, y + 0.5])
            weights = barycentric_coordinates(pixel_center, a, b, c)

            if weights is None:
                continue

            alpha, beta, gamma = weights

            if alpha >= 0 and beta >= 0 and gamma >= 0:
                depth = alpha * depth_a + beta * depth_b + gamma * depth_c
                yield x, y, depth


def render(vertices, faces, frame_width, frame_height):
    camera_position = numpy.array([3.0, 2.0, 5.0])
    target = centroid(vertices)
    screen_vertices, depths = project_vertices(
        vertices,
        camera_position,
        target,
        frame_width,
        frame_height,
    )

    background_color = (245, 245, 245)
    edge_color = (40, 40, 40)
    image = Image.new("RGB", (frame_width, frame_height), background_color)
    pixels = image.load()
    z_buffer = numpy.full((frame_height, frame_width), numpy.inf)
    face_colors = [
        (236, 93, 87),
        (247, 178, 103),
        (246, 216, 117),
        (104, 190, 141),
        (88, 164, 176),
        (116, 145, 207),
    ]

    for face_index, face in enumerate(faces):
        color = face_colors[face_index // 2 % len(face_colors)]
        triangle_pixels = screen_vertices[face]
        triangle_depths = depths[face]

        for x, y, depth in pixels_inside_triangle(
            triangle_pixels,
            triangle_depths,
            frame_width,
            frame_height,
        ):
            if depth < z_buffer[y, x]:
                z_buffer[y, x] = depth
                pixels[x, y] = color

    edge_pixels = []

    for y in range(1, frame_height - 1):
        for x in range(1, frame_width - 1):
            color = pixels[x, y]

            if color == background_color:
                continue

            neighbors = [
                pixels[x - 1, y],
                pixels[x + 1, y],
                pixels[x, y - 1],
                pixels[x, y + 1],
            ]

            if any(neighbor != color for neighbor in neighbors):
                edge_pixels.append((x, y))

    for x, y in edge_pixels:
        pixels[x, y] = edge_color

    return image


def main():
    frame_width = 800
    frame_height = 600
    vertices, faces = parse_obj_file(PATH_TO_OBJ_FILE)
    image = render(vertices, faces, frame_width, frame_height)
    image.save(PATH_TO_OUTPUT_IMAGE)
    print(f"Rendered {PATH_TO_OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()
