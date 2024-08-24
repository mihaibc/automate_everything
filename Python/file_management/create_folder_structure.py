import os

def create_folder_structure(base_path, folder_structure):
    """
    Creates a folder structure based on the provided dictionary.

    :param base_path: The root directory where the structure will be created.
    :param folder_structure: A dictionary defining the folder structure.
    """
    for main_folder, sub_folders in folder_structure.items():
        for sub_folder in sub_folders:
            path = os.path.join(base_path, main_folder, sub_folder)
            os.makedirs(path, exist_ok=True)
            print(f"Created: {path}")

if __name__ == "__main__":
    # Define the base path where the folder structure will be created
    base_path = input("Enter the base path where the folder structure should be created: ").strip()
    
    # Define the folder structure
    folder_structure = {
        "Python": ["file_management", "web_scraping", "data_processing", "system_administration"],
        "Go": ["cloud_automation", "ci_cd"],
        "C++": ["performance_critical", "low_level_system"],
        "Perl": ["text_processing", "web_scraping"],
        "Bash": ["system_administration", "file_management", "automation_scripts"],
        "PowerShell": ["windows_automation", "system_administration", "active_directory"],
    }

    # Create the folder structure
    create_folder_structure(base_path, folder_structure)