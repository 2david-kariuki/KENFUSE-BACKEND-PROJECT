#!/usr/bin/env python3
"""
KENFUSE Backend Server
End of Life Planning Platform for Kenya
"""

import os
from app import create_app

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create Flask app
app = create_app()

@app.route('/')
def index():
    return {
        'service': 'KENFUSE - End of Life Planning Platform',
        'version': '1.0.0',
        'status': 'running',
        'description': 'Digital platform for wills, memorials, fundraising, and vendor marketplace',
        'country': 'Kenya',
        'endpoints': {
            'auth': '/api/auth',
            'wills': '/api/wills',
            'memorials': '/api/memorials',
            'fundraisers': '/api/fundraisers',
            'vendors': '/api/vendors',
            'payments': '/api/payments',
            'admin': '/api/admin'
        },
        'admin': {
            'email': 'admin@kenfuse.com',
            'password': 'Admin@123'
        }
    }

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 KENFUSE BACKEND SERVER")
    print("="*60)
    print("📡 Server: http://localhost:5000")
    print("🔐 API Base: http://localhost:5000/api")
    print("💾 Database: PostgreSQL/SQLite")
    print("👑 Admin: admin@kenfuse.com / Admin@123")
    print("="*60 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    )
