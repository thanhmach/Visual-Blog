from app.routes import app  # Import the app instance

if __name__ == '__main__':
    app.config['MYSQL_HOST'] = "localhost" 
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = ""
    app.config['MYSQL_DB'] = "blogdb"
    
    app.run(debug=True)