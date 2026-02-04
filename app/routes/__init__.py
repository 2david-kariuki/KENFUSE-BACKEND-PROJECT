# Import all routes
from .auth import auth_bp
from .wills import wills_bp
from .memorials import memorials_bp

# Export blueprints
__all__ = ['auth_bp', 'wills_bp', 'memorials_bp']
