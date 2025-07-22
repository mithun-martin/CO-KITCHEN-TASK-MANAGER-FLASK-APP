import enum
from flask import Flask, render_template, request, redirect
#👉 This imports Flask (the web framework), render_template (to show HTML pages), and request (to read form data sent by user).
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from werkzeug.exceptions import BadRequest


app = Flask(__name__)
#1)👉 This creates your Flask application object — it runs your web server.


@app.template_filter('ksa_time')
def convert_to_ksa(dt):
    if dt is None:
        return ""
    saudi_tz = pytz.timezone('Asia/Riyadh')
    ksa_time = dt.astimezone(saudi_tz)
    return ksa_time.strftime('%I:%M %p')

#dont byehart or laer thus code only this to sve time ksa time that why added

#to itialize sql alchemy" the followig line suse chatgpt or  documentatons neo need to byehart
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mithun@localhost:5432/hotel_ops'
import os
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
#done above for heroku since it will not work on local machine dont byehet code
uri = os.environ.get("DATABASE_URL","postgresql://postgres:Mithun@localhost:5432/hotel_ops")  # Heroku provides this
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri





#👉 This tells Flask where your database will be.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #dont think much here


#2)SETTING UP THE DATABASE  
db = SQLAlchemy(app)
#📌 What is SQLAlchemy here?
#It’s the ORM (Object Relational Mapper) you’re using to connect your Python code to a database.
#In this case, you’re using SQLite as the database, and SQLAlchemy is the library that lets you interact with it via Python classes instead of raw SQL queries.
#the line here ✅ Initializes SQLAlchemy for your Flask app.

class Branche_issues(enum.Enum):
    Baladia_Card = "Baladia_Card"
    Water_Supply = "Water_Supply"
    Air_Conditioning = "Air_Conditioning"
    Chiller = "Chiller"
    Freezer = "Freezer"
    Sign_Board = "Sign_Board"
    Robot = "Robot"
    Uniform = "Uniform"
    Fresh_Air = "Fresh_Air"
    Exhaust = "Exhaust"
    Pest_Control = "Pest_Control"
    Duct_Cleaning = "Duct_Cleaning"
    Air_Curtain = "Air_Curtain"
    Ceiling_Lights = "Ceiling_Lights"
    Floor_Tiles = "Floor_Tiles"
    DeskTop_no_charge = "DeskTop_no_charge"
    Salad_chiller = "Salad_chiller"
    Electrical_and_Plumbing = "Electrical_&_Plumbing"
    Expired_Products = "Expired_Products"
    Oil_Status = "Oil_Status"
    Food_Safety = "Food_Safety"
    Personal_Hygiene = "Personal_Hygiene"
    Dry_Stock_Room = "Dry_Stock_Room"
    Others = "Others"  # ✅ Added this line to handle the "Others" category



class Branches(enum.Enum):
    Sahafa = "Sahafa"              
    Sulimania = "Sulimania"
    Rabwah = "Rabwah"
    Rawdah = "Rawdah"
    Ishbiliya = "Ishbiliya"
    Suwaidi = "Suwaidi"
    Laban = "Laban"
    Alhasa = "Alhasa"
    Dammam = "Dammam"
    Khobar  = "Khobar"
    Qassim = "Qassim"
    Hail = "Hail"
    Jeddah = "Jeddah"
  

class HotelOp(db.Model):
    #👉 A Python class defining your ToDo table basically MODEL LIEK IN SB
    __tablename__ = 'hotel_op'  # 👈 This is the new table name
    sno = db.Column(db.Integer,primary_key = True) #defining the primary key
    branch_issues = db.Column(db.Enum(Branche_issues), nullable = False)
    desc = db.Column(db.String(500),nullable = False)
    status = db.Column(db.String(50), nullable=False, default="None")        # ✅ New
    # date_created = db.Column(db.DateTime,default = datetime.utcnow)
    branches = db.Column(db.Enum(Branches), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False)
    remarks = db.Column(db.String(200))  # ✅ New
    # date_created = db.Column(db.DateTime, nullable=False) # ✅ New

with app.app_context():
    db.create_all()


    # def __repr__(self) -> str: #not much think agin
    #     return f"{self.sno} - {self.title}"
    #__repr__ is a special method in Python used to define what the "official string representation" of an object should be 
    #(what you see when you type print(todo) in consle fore easy debuggig



#4)defining routes
@app.route("/", methods=["GET", "POST"])
def create_read():
    if request.method == 'POST':
        #branch_issues = request.form["branch_issues"]
       # You're assigning a string, but SQLAlchemy expects the actual Enum type Branche_issues, not a plain string
            
        branch_issues_str = request.form['branch_issues']
        try:
            branch_issues = Branche_issues(branch_issues_str)
        except ValueError:
            raise BadRequest("Invalid branch issue selected")



        desc = request.form['desc']
        status = request.form['status']
        branches = request.form['Branch']
        saudi_tz = pytz.timezone('Asia/Riyadh')
        current_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(saudi_tz)
        remarks = request.form.get('remarks', '')  # Get remarks if provided, else empty string
        #since for all others we gav emandatory to fill else form wont e netering we saw in ui
        #as nullable = False but for remarks we did not do it so it can be empty

        hotelop = HotelOp(branch_issues=branch_issues, desc=desc, status=status, branches=branches, date_created=current_time, remarks=remarks)
        db.session.add(hotelop)  # Add the new ToDo item to the session
        db.session.commit()
        return redirect("/")  # Important to redirect after POST

    # GET request — check if filter applied via ?filter_branch
    filter_branch = request.args.get('filter_branch')

    if filter_branch and filter_branch != 'All':
        allToDo = HotelOp.query.filter_by(branches=filter_branch).all()
    else:
        allToDo = HotelOp.query.all()

    return render_template("index.html", allToDo=allToDo, Branches=Branches, selected_branch=filter_branch,Branche_issues=Branche_issues)


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = HotelOp.query.get_or_404(sno)

    if request.method == "POST":
        branch_issues_str = request.form["branch_issues"]
        try:
            todo.branch_issues = Branche_issues(branch_issues_str)
        except ValueError:
            raise BadRequest("Invalid branch issue selected")

        todo.desc = request.form["desc"]
        todo.status = request.form["status"]
        todo.remarks = request.form.get("remarks", "")
        todo.branches = Branches(request.form["Branch"])  # ✅ This line was missing before

        db.session.commit()
        return redirect("/")

    return render_template("update.html", todo=todo, Branche_issues=Branche_issues, Branches=Branches)




@app.route("/delete/<int:sno>")
def delete(sno):   
    record = HotelOp.query.get(sno)
    if record is None:
        return "Record not found", 404
    
    db.session.delete(record)
    db.session.commit()
    return redirect("/") #after deleting come back to home page



if __name__ == "__main__":
    app.run(debug=True)


   #THESE LINES TELL APP TO RUN AND IN DEBUGGER MODE SO THAT IF ANY ERRO HAPPENS IT WILLL BE SHOW IN BROWSER

#📦 2️Create a .gitignore file
#Very important — to ignore files you don’t want to push (like your DB, virtual env)