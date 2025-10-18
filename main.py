import os
import cv2
import numpy as np
import cv2.aruco as aruco

def align_and_scale_poster(image, poster, scale_factor=4.0):
    marker_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
    corners, ids, _ = aruco.detectMarkers(image, marker_dict)

    if ids is not None and len(ids) > 0:
        aruco.drawDetectedMarkers(image, corners)
        c1, c2, c3, c4 = corners[0][0]  # Top-left, top-right, bottom-right, bottom-left

        height_marker = int(np.linalg.norm(c1 - c4))  # Height of the marker
        width_marker = int(np.linalg.norm(c1 - c2))  

        height, width = poster.shape[:2]
        scaled_height = int(height * scale_factor)
        scaled_width = int(width * scale_factor)
        poster = cv2.resize(poster, (scaled_width, scaled_height))
        x_offset = (scaled_width - width) // 2
        y_offset = (scaled_height - height) // 2
        poster_corners = np.array([[x_offset, y_offset], [scaled_width - x_offset, y_offset], 
                                   [scaled_width - x_offset, scaled_height - y_offset], 
                                   [x_offset, scaled_height - y_offset]], dtype="float32")

        transform_matrix = cv2.getPerspectiveTransform(poster_corners, np.array([c1, c2, c3, c4], dtype="float32"))
        warped_poster = cv2.warpPerspective(poster, transform_matrix, (image.shape[1], image.shape[0]))

        warped_poster_gray = cv2.cvtColor(warped_poster, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(warped_poster_gray, 1, 255, cv2.THRESH_BINARY)

        # Combine the warped poster and the original image
        inverse_mask = cv2.bitwise_not(mask)
        background = cv2.bitwise_and(image, image, mask=inverse_mask)
        foreground = cv2.bitwise_and(warped_poster, warped_poster, mask=mask)
        result = cv2.add(background, foreground)

        return result, warped_poster_gray, inverse_mask, background, foreground
    else:
        print("No markers detected.")
        return image, None, None, None, None

folder_path = r"C:\Users\ATHARVA\Downloads\Github"
os.makedirs(folder_path, exist_ok=True)

# Loop for processing input images
for i in range(1, 11):  # Adjust the range based on the number of images you have
    # Load images
    Augmented_Img = cv2.imread("poster 1 .jpg")  # Poster image
    Image = cv2.imread(f"input _images/image{i}.jpg")  # Input image

    # Check if images are loaded properly
    if Augmented_Img is None:
        print(f"Failed to load poster image.")
        continue
    if Image is None:
        print(f"Failed to load image{i}.jpg.")
        continue

    # Align and scale the poster to fit the ArUco marker
    result, warped_poster_gray, inverse_mask, background, foreground = align_and_scale_poster(Image, Augmented_Img)

    # Save the final result and intermediate outputs
    destination_path = rf"output_images{i}.jpg"
    if cv2.imwrite(destination_path, result):
        print(f"Image saved as {destination_path}")
    else:
        print("Failed to save the image.")

    # Base output directory
base_path = r"C:\Users\ATHARVA\Downloads\Github"

# Subfolders for each output type
paths = {
    "result": os.path.join(base_path, "results"),
    "poster": os.path.join(base_path, "wrapped_poster"),
    "mask": os.path.join(base_path, "inverse_mask"),
    "background": os.path.join(base_path, "background"),
    "foreground": os.path.join(base_path, "foreground")
}

# Create all folders
for path in paths.values():
    os.makedirs(path, exist_ok=True)

# Loop for processing input images
for i in range(1, 11):
    Augmented_Img = cv2.imread("poster 1 .jpg")
    Image = cv2.imread(f"input _images/image{i}.jpg")

    if Augmented_Img is None:
        print(f"Failed to load poster image.")
        continue
    if Image is None:
        print(f"Failed to load image{i}.jpg.")
        continue

    result, warped_poster_gray, inverse_mask, background, foreground = align_and_scale_poster(Image, Augmented_Img)

    cv2.imwrite(os.path.join(paths["result"], f"output_image{i}.jpg"), result)
    if warped_poster_gray is not None:
        cv2.imwrite(os.path.join(paths["poster"], f"wrapped_poster{i}.jpg"), warped_poster_gray)
    if inverse_mask is not None:
        cv2.imwrite(os.path.join(paths["mask"], f"inverse_mask{i}.jpg"), inverse_mask)
    if background is not None:
        cv2.imwrite(os.path.join(paths["background"], f"background{i}.jpg"), background)
    if foreground is not None:
        cv2.imwrite(os.path.join(paths["foreground"], f"foreground{i}.jpg"), foreground)

cv2.destroyAllWindows()