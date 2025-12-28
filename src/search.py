import cv2
import os
import argparse

def search_and_highlight(directory_path, target_image_path, threshold=0.95):
    # Load the target image
    target = cv2.imread(target_image_path)
    if target is None:
        print(f"Error: Could not open target image '{target_image_path}'")
        return

    th, tw = target.shape[:2]

    # Filter for image files first to get a total count
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')
    files_to_process = [f for f in os.listdir(directory_path)
                        if f.lower().endswith(valid_extensions)]

    total_files = len(files_to_process)
    if total_files == 0:
        print(f"No valid images found in {directory_path}")
        return

    # Create output directory
    output_dir = "search_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Starting search for '{os.path.basename(target_image_path)}' in {total_files} files...\n")

    found_count = 0

    for index, filename in enumerate(files_to_process, start=1):
        # Progress indicator
        print(f"[{index}/{total_files}] Processing: {filename}", end="\r")

        collage_path = os.path.join(directory_path, filename)
        collage = cv2.imread(collage_path)

        if collage is None:
            continue

        # Template matching
        result = cv2.matchTemplate(collage, target, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            found_count += 1
            # Clear the current progress line to print the match result
            print(f"\n >> MATCH FOUND: {filename} (Confidence: {max_val:.2%})")

            # Draw box and save
            top_left = max_loc
            bottom_right = (top_left[0] + tw, top_left[1] + th)
            cv2.rectangle(collage, top_left, bottom_right, (0, 0, 255), 5)

            output_path = os.path.join(output_dir, f"found_{filename}")
            cv2.imwrite(output_path, collage)

    print(f"\n\nSearch Complete.")
    print(f"Total matches found: {found_count}")
    if found_count > 0:
        print(f"Check the '{output_dir}' folder for highlighted results.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and highlight an image within a collage with progress tracking.")
    parser.add_argument("directory", type=str, help="Path to collage directory")
    parser.add_argument("image", type=str, help="Path to target image")
    parser.add_argument("--threshold", type=float, default=0.95, help="Matching threshold (default 0.95)")

    args = parser.parse_args()
    search_and_highlight(args.directory, args.image, args.threshold)
