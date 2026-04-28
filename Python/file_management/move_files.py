import os
import shutil


def move_files(src_folder, dest_folder, file_extensions):
    """
    Moves files with specified extensions from the source folder to the destination folder.

    :param src_folder: The directory to search for files.
    :param dest_folder: The directory where files should be moved.
    :param file_extensions: A list of file extensions to move.
    """
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file.lower().endswith(tuple(file_extensions)):
                file_path = os.path.join(root, file)
                shutil.move(file_path, dest_folder)
                print(f"Moved: {file_path} to {dest_folder}")


if __name__ == "__main__":
    source_folder = input("Enter the source folder path: ").strip()
    destination_folder = input("Enter the destination folder path: ").strip()
    extensions = input("Enter the file extensions to move (comma-separated, e.g., pdf,epub): ").strip().split(',')

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Created destination folder: {destination_folder}")

    move_files(source_folder, destination_folder, extensions)
