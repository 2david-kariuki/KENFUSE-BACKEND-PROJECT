import sys
sys.path.insert(0, '.')

print("Testing import chain...")
print("1. Testing app.pdf_utils import...")
try:
    from app.pdf_utils import PDFGenerator
    print("✓ PDFGenerator import successful")
except ImportError as e:
    print(f"✗ PDFGenerator import failed: {e}")

print("\n2. Testing app.routes.memorials import...")
try:
    from app.routes import memorials
    print("✓ memorials import successful")
except ImportError as e:
    print(f"✗ memorials import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing app.routes.__init__ import...")
try:
    from app.routes import memorials_bp
    print("✓ memorials_bp import successful")
except ImportError as e:
    print(f"✗ memorials_bp import failed: {e}")
