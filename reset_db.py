import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()

with app.app_context():
    print("🔄 Resetting database...")
    
    # Drop all tables
    db.drop_all()
    print("✓ Dropped all tables")
    
    # Create all tables
    db.create_all()
    print("✓ Created all tables")
    
    # Create admin user with unique phone
    admin = User(
        email='admin@kenfuse.com',
        phone='+254700000001',  # Changed from 000000
        first_name='Admin',
        last_name='Kenfuse',
        role='admin',
        is_verified=True,
        is_active=True,
        created_at=datetime.utcnow()
    )
    admin.set_password('Admin@123')
    db.session.add(admin)
    db.session.commit()
    print("✓ Created admin user")
    
    print("\n✅ Database reset complete!")
    print("Admin credentials:")
    print("  Email: admin@kenfuse.com")
    print("  Password: Admin@123")
    print("  Phone: +254700000001")
