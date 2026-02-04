import sys
sys.path.insert(0, '.')

print("Testing app.models import...")
try:
    import app.models
    print("Contents of app.models:", dir(app.models))
except Exception as e:
    print(f"Error: {e}")

print("\n\nTesting db import from app...")
try:
    from app import db
    print("db imported successfully from app")
except Exception as e:
    print(f"Error importing db from app: {e}")

print("\n\nTesting Memorial import...")
try:
    from app.models import Memorial
    print("Memorial imported successfully")
except Exception as e:
    print(f"Error importing Memorial: {e}")
