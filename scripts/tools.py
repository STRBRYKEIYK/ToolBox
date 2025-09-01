"""
WorkBox Tools Menu
=================

This script provides a menu to access various WorkBox utilities and tools.
"""

import os
import sys
import subprocess

# Set up path for imports
script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'-' * len(text)}{Colors.ENDC}")

def print_menu():
    """Print the main menu"""
    print_header("WorkBox Tools Menu")
    print("1. Initialize Database")
    print("2. Test System")
    print("3. Network Test")
    print("4. Manage Database Connection")
    print("5. Update Database Connection")
    print("6. Set Up MySQL")
    print("7. Run Client Test")
    print("0. Exit")

def run_script(script_name, description):
    """Run a Python script with proper error handling"""
    print_header(f"Running {description}")
    script_path = os.path.join(script_dir, script_name)
    
    try:
        # Use sys.executable to ensure the same Python interpreter is used
        result = subprocess.run([sys.executable, script_path])
        if result.returncode != 0:
            print(f"\n{Colors.FAIL}Script exited with error code {result.returncode}{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Error running script: {e}{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}Press Enter to return to menu...{Colors.ENDC}")
    input()

def main():
    """Main function"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_menu()
        
        try:
            choice = input("\nEnter your choice (0-7): ")
            
            if choice == '1':
                run_script("init_db.py", "Database Initialization")
            elif choice == '2':
                run_script("test_system.py", "System Test")
            elif choice == '3':
                run_script("network_test.py", "Network Test")
            elif choice == '4':
                run_script("manage_connection.py", "Connection Manager")
            elif choice == '5':
                run_script("update_db_connection.py", "Update Database Connection")
            elif choice == '6':
                run_script("setup_mysql.py", "MySQL Setup")
            elif choice == '7':
                run_script("client.py", "Client Test")
            elif choice == '0':
                print(f"\n{Colors.GREEN}Thank you for using WorkBox Tools. Goodbye!{Colors.ENDC}")
                break
            else:
                print(f"\n{Colors.WARNING}Invalid choice. Please enter a number between 0 and 7.{Colors.ENDC}")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Exiting due to user interrupt. Goodbye!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
