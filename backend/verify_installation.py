"""
Verify Installation Script
Run this to check if all dependencies are properly installed
"""
import sys

def check_import(module_name, package_name=None):
    """Try to import a module and report status"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name:20} - Installed")
        return True
    except ImportError as e:
        print(f"❌ {package_name:20} - Missing")
        print(f"   Error: {str(e)}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    import os
    if os.path.exists(file_path):
        print(f"✅ {description:20} - Found")
        return True
    else:
        print(f"❌ {description:20} - Not found")
        print(f"   Path: {file_path}")
        return False

def main():
    print("=" * 60)
    print("  Smart Toll Plaza - Installation Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python version
    print("📦 Python Version:")
    print(f"   {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")
        all_good = False
    print()
    
    # Check required packages
    print("📦 Required Packages:")
    packages = [
        ("django", "Django"),
        ("rest_framework", "Django REST Framework"),
        ("celery", "Celery"),
        ("cv2", "OpenCV"),
        ("ultralytics", "YOLOv8 (Ultralytics)"),
        ("PIL", "Pillow"),
        ("dotenv", "python-dotenv"),
        ("sqlalchemy", "SQLAlchemy"),
    ]
    
    for module, name in packages:
        if not check_import(module, name):
            all_good = False
    
    print()
    
    # Check configuration files
    print("📝 Configuration Files:")
    import os
    backend_path = os.path.dirname(os.path.abspath(__file__))
    
    configs = [
        (os.path.join(backend_path, ".env"), ".env file"),
        (os.path.join(backend_path, "db.sqlite3"), "SQLite database"),
    ]
    
    for file_path, desc in configs:
        check_file_exists(file_path, desc)
    
    print()
    
    # Check model file
    print("🤖 YOLO Model:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        model_path = os.getenv("YOLO_MODEL_PATH", "")
        if model_path:
            if check_file_exists(model_path, "YOLO Model (.pt)"):
                # Check file size
                size_mb = os.path.getsize(model_path) / (1024 * 1024)
                print(f"   Size: {size_mb:.2f} MB")
            else:
                all_good = False
                print("   Update YOLO_MODEL_PATH in .env file")
        else:
            print("❌ YOLO_MODEL_PATH not set in .env")
            all_good = False
    except Exception as e:
        print(f"❌ Error checking model: {str(e)}")
        all_good = False
    
    print()
    
    # Check .env settings
    print("⚙️  Critical Settings:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        eager_mode = os.getenv("USE_EAGER_CELERY", "").lower()
        if eager_mode == "false":
            print("✅ USE_EAGER_CELERY   - false (Async mode enabled)")
        else:
            print(f"⚠️  USE_EAGER_CELERY   - {eager_mode} (Should be 'false')")
            all_good = False
        
        debug_mode = os.getenv("DEBUG", "").lower()
        print(f"   DEBUG              - {debug_mode}")
        
    except Exception as e:
        print(f"❌ Error reading .env: {str(e)}")
        all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("✅ ALL CHECKS PASSED! System ready to run.")
        print()
        print("Next steps:")
        print("1. Terminal 1: celery -A smarttoll worker --loglevel=info --pool=solo")
        print("2. Terminal 2: python manage.py runserver")
    else:
        print("❌ SOME CHECKS FAILED! Please fix the issues above.")
        print()
        print("To install missing packages:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
