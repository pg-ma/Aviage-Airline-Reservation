from myapp import app,db
from myapp.admin import admin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from myapp.models import *



if __name__ == "__main__":
    #app.run(debug=True)
    with app.app_context(): #create the database, if not already created
        db.create_all()
       
    
    admin.init_app(app)
    
    
    
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=True)
    #hello
    #line 2
    #line 3
    #line 4
    #Line 5
