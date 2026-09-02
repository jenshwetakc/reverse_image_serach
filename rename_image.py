import os
def rename_images(directory_path):

    # name the gui element
    prefix = "background"

    # List all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Filter only image files (optional extensions)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]

    # Sort to keep renaming order consistent
    image_files.sort()

    for i, filename in enumerate(image_files, 1):
        # Get file extension
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{i}{ext}"

        src = os.path.join(directory_path, filename)
        dst = os.path.join(directory_path, new_name)

        os.rename(src, dst)
        print(f"Renamed: {filename} → {new_name}")

# Replace with your directory path
rename_images("/seed/background")

