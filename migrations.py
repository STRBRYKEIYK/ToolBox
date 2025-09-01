"""
WorkBox Database Migration Tool
==============================

This script helps manage database migrations to keep schema changes organized.
It uses Alembic, a lightweight database migration tool for SQLAlchemy.
"""

import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define constants
ALEMBIC_DIR = os.path.join(os.path.dirname(__file__), "alembic")


def setup_alembic():
    """Initialize Alembic in the project if not already set up"""
    if not os.path.exists(ALEMBIC_DIR):
        print("⚙️ Setting up Alembic for database migrations...")
        
        # Create alembic directory
        os.makedirs(ALEMBIC_DIR, exist_ok=True)
        
        # Initialize alembic
        result = subprocess.run(
            ["alembic", "init", "alembic"],
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to initialize Alembic:")
            print(result.stderr)
            return False
        
        # Update alembic.ini file with database URL
        alembic_ini = os.path.join(os.path.dirname(__file__), "alembic.ini")
        if os.path.exists(alembic_ini):
            with open(alembic_ini, "r") as f:
                content = f.read()
            
            # Replace SQLite URL with our MySQL URL
            db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/workbox_db")
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                f"sqlalchemy.url = {db_url}"
            )
            
            with open(alembic_ini, "w") as f:
                f.write(content)
        
        print("✅ Alembic setup complete")
    else:
        print("✓ Alembic is already set up")
    
    return True


def create_migration(message):
    """Create a new migration with a message"""
    print(f"📝 Creating migration: {message}")
    
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Failed to create migration:")
        print(result.stderr)
        return False
    
    print("✅ Migration created successfully")
    return True


def apply_migrations():
    """Apply all pending migrations"""
    print("🔄 Applying all pending migrations...")
    
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Failed to apply migrations:")
        print(result.stderr)
        return False
    
    print("✅ All migrations applied successfully")
    return True


def rollback_migration(steps=1):
    """Rollback the last migration or specified number of steps"""
    print(f"⏪ Rolling back {steps} migration(s)...")
    
    result = subprocess.run(
        ["alembic", "downgrade", f"-{steps}"],
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Failed to rollback migration:")
        print(result.stderr)
        return False
    
    print("✅ Rollback completed successfully")
    return True


def show_history():
    """Show migration history"""
    print("📜 Migration history:")
    
    result = subprocess.run(
        ["alembic", "history", "--verbose"],
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Failed to show history:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    return True


def main():
    """Main CLI entrypoint"""
    parser = argparse.ArgumentParser(description="WorkBox Database Migration Tool")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Migration command")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup Alembic for migrations")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply all pending migrations")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument(
        "--steps", type=int, default=1, help="Number of migrations to roll back"
    )
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "setup":
        setup_alembic()
    elif args.command == "create":
        if not setup_alembic():
            return
        create_migration(args.message)
    elif args.command == "apply":
        if not setup_alembic():
            return
        apply_migrations()
    elif args.command == "rollback":
        if not setup_alembic():
            return
        rollback_migration(args.steps)
    elif args.command == "history":
        if not setup_alembic():
            return
        show_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
