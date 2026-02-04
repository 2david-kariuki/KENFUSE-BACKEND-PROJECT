#!/bin/bash

echo "========================================="
echo "🎯 KENFUSE BACKEND SETUP"
echo "========================================="

# Create virtual environment
echo "1. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "2. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory
echo "3. Creating uploads directory..."
mkdir -p uploads

# Setup PostgreSQL (optional)
echo "4. Setting up database..."
read -p "Use SQLite (easier) or PostgreSQL? (sqlite/postgres): " db_choice

if [[ "$db_choice" == "postgres" ]]; then
    echo "Installing PostgreSQL..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
    
    echo "Creating database and user..."
    sudo -u postgres psql -c "CREATE DATABASE kenfuse_db;"
    sudo -u postgres psql -c "CREATE USER kenfuse WITH PASSWORD 'password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kenfuse_db TO kenfuse;"
    
    echo "Using PostgreSQL database..."
else
    echo "Using SQLite database..."
    # Update .env to use SQLite
    sed -i 's|postgresql://.*|sqlite:///kenfuse.db|' .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Test endpoints:"
echo "  curl http://localhost:5000"
echo "  curl -X POST http://localhost:5000/api/auth/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\":\"test@kenfuse.com\",\"phone\":\"+254712345678\",\"first_name\":\"Test\",\"last_name\":\"User\",\"password\":\"Test@123\"}'"
