#!/usr/bin/env python3
import importlib.util

# List of required modules and their installation commands
required_modules = {
    'sys': None,  # Standard library modules do not require installation.
    'logging': None,
    'subprocess': None,
    'tkinter': 'python3-tk',  # This might require installation on some systems.
    'qrcode': 'pip install qrcode[pil]',
    'fpdf': 'pip install fpdf',
}

def check_module(module_name):
    """
    Check if a module can be imported without actually importing it.
    Returns True if the module is available, False otherwise.
    """
    module_spec = importlib.util.find_spec(module_name)
    return module_spec is not None

def main():
    # Track if all modules are available
    all_modules_available = True

    print("Checking for required Python modules...")

    # Check each module
    for module, install_command in required_modules.items():
        if check_module(module):
            print(f"Module '{module}' is present.")
        else:
            print(f"Module '{module}' is MISSING.")
            if install_command:
                print(f"To install, run: {install_command}")
            all_modules_available = False

    # If a module is missing, inform the user.
    if not all_modules_available:
        print("\nOne or more modules are missing. Please install the missing modules to run the script.")
    else:
        print("\nAll required modules are present. You can run the script.")

if __name__ == "__main__":
    main()
