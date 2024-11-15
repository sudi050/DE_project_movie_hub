# main.py
from config_db_admin import server
from flask_auth import login_manager
from flask_admin_dashboard import admin_bp  # Import the admin blueprint here

# Register the admin blueprint
server.register_blueprint(admin_bp)

if __name__ == "__main__":
    server.run(debug=True)
