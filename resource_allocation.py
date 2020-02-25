from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt
import json
from flask import jsonify
import datetime
from dateutil.parser import parse

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://aakarshachug:aakarsha123@cluster0-qtf6n.mongodb.net/test?retryWrites=true&w=majority")
db = client.resource_allocation

@app.route('/')
def index():
    if 'username' in session:
        s = session['username']
        return render_template('index_dashboard.html' , name = s)

    return render_template('index.html')

#Logout---------------------------------------------------------------
@app.route('/logout' , methods = ['POST'])
def logout():
    session.pop('username' ,None)
    return redirect(url_for('index'))

# Login--------------------------------------------------------------   
@app.route('/login', methods=['POST','GET'])
def login():
    users = db.user_credentials
    login_user = users.find_one({'username' : request.form['username-login']})

    if login_user:
        #if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
         user_pass = login_user['password']
         if bcrypt.checkpw(request.form['password-login'].encode('utf-8'), user_pass):
            session['username'] = request.form['username-login']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

# Register-------------------------------------------------------
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = db.user_credentials
        existing_user = users.find_one({'username' : request.form['username-register']})
        existing_email = users.find_one({'email' : request.form['email-register']}) 

        if existing_user is None and existing_email is None:
            #hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            hashpass = bcrypt.hashpw(request.form['password-register'].encode('utf8'), bcrypt.gensalt())
            users.insert({'username' : request.form['username-register'], 'password' : hashpass , 'email' :request.form['email-register'] })
            session['username'] = request.form['username-register']
            return redirect(url_for('index'))
        
        return 'That username or email already exists!'

    return render_template('index.html')

@app.route('/displaymyresource', methods=["POST","GET"])
def displaymyresources():
    print("ddg")
    if request.method == 'POST':
        print("yesss")
        resources = db.resources
        print("hello")
        s = session['username']
        print(s)
        result = []
        
        for document in resources.find({"slot_info.blocked_by" : s}):
            ans = {'resource' : document['r_name']  , 'status' : "blocked by you",
            'end_time' : document['slot_info']['end_time']
            }
            result.append(ans)
        
        print("display my resource----", result)
        my_resource_length = len(result)
         
        return jsonify({'resources' : result , 'my_resource_length' : my_resource_length})

#Fetch all resources for the user---------------------------------

@app.route('/allresources', methods=['POST'])
def allresources():
    if request.method == 'POST':
        resources = db.resources
        task = db.tasks
        s = session['username']
        result = []

        requested = []

        for document in task.find({"requested_by" : s , "status" : "pending"}):
            requested.append(document['resource'])
        
        for document in resources.find():
            if document['r_name'] in requested:
                ans = {'resource' : document['r_name']  , 'status' : document['status'],
                'booked_by' : document['slot_info']['blocked_by'],
                'end_time' : document['slot_info']['end_time'],
                 'request_status' : "pending",
                 'session' : s
              }

            else:
                 ans = {'resource' : document['r_name']  , 'status' : document['status'],
                'booked_by' : document['slot_info']['blocked_by'],
                'end_time' : document['slot_info']['end_time'],
                 'request_status' : "not-requested",
                 'session' : s
              }
            
            result.append(ans)
        
        all_resource_length =  len(result)
        print("All Resources result---", result)
         
        return jsonify({'resources' : result , 'all_resource_length' : all_resource_length })

# Fetch all the pending tasks for the user-------------------------
@app.route('/alltasks', methods=['POST'])
def alltasks():
    if request.method == 'POST':
        tasks = db.tasks
        result = []
        s = session['username']
        #doc = tasks.find({'requested_to' : s} , limit=10).sort(sort)
        doc = tasks.find({"$query" : {'requested_to' : s , "status" : "pending"}, "$orderby" : {"request_time": 1}})
        for document in doc:
            ans = {'resource' : document['resource']  , 'status' : document['status'],
            'requested_by' : document['requested_by'],
            'requested_time' : document["request_time"]
            
             }
            result.append(ans)
        
        all_task_length = len(result)
        
        print("Task Result-----", result)
         
        return jsonify({'resources' : result , 'all_task_length': all_task_length })

#Request a booked resource from the owner----------------------------

@app.route('/requestresource', methods=['POST'])
def requestresource():
    if request.method == 'POST':
        s = session['username']
        x = request.get_json()
        r_json = x['r_name']
        s_json = x['status']
        endtime = x['end_time']
        end_datetime = parse(endtime)


        
        if s_json == "available":
            resources = db.resources

            print("yoooo")
            resources.update_one({"r_name" : r_json } , {"$set": {"status" : "booked" ,"slot_info" : {

                "start_time" : datetime.datetime.now(),
                "end_time" : end_datetime,
                "blocked_by" : s
                
            }}})

        else:
            task = db.tasks
            owner = x["blocked_by"]
            task.insert({"requested_by" : s , "requested_to" : owner , "status" : "pending" ,

            "resource" : r_json , "request_time" : datetime.datetime.now() , "end_time" : end_datetime
            
             })



        return jsonify({'status':'got it'})

# Approve a requested resource----------------------------------------------------------
@app.route('/approveresource', methods=['POST'])
def approveresource():
    if request.method == 'POST':
        s = session['username']
        resources = db.resources
        tasks = db.tasks
        x = request.get_json()
        r_json = x['r_name']
       
        new_owner = x['requested_by']
        

        print("For Debugging")
        print(r_json)

        doc = tasks.find_one({"resource" : r_json , "requested_by" : new_owner , "requested_to" : s })
        print(doc['_id'])

        tasks.update_one({"_id" :  doc['_id']} , 
         {"$set": {"status" : "approved"}})

        resources.update_one({"r_name" : r_json} , {"$set" : {"slot_info" : {

                "start_time" : datetime.datetime.now(),
                "end_time" : doc['end_time'],
                "blocked_by" : new_owner } }})
        
        bulk = tasks.initialize_unordered_bulk_op()

        bulk.find({"resource" : r_json , "requested_to" : s , "status" : "pending"}).update({ "$set": { "requested_to": new_owner} })
        bulk.execute()

        return jsonify({"status" : "approved!"})
        



@app.route('/releaseresource', methods=['POST'])
def releaseresource():
    if request.method == 'POST':
        s = session['username']
        x = request.get_json()
        r_json = x['r_name']
        resources = db.resources
        tasks = db.tasks
        doc = tasks.find( {'resource' : r_json, 'status' : 'pending'})
        print(doc.count())
        
        if doc.count() > 0:
            doc = doc.sort("request_time" , 1)
            new_owner_doc = doc[0]
            resources.update_one({"r_name" : r_json} , {"$set" : {"slot_info" : {

                "start_time" : datetime.datetime.now(),
                "end_time" : new_owner_doc['end_time'],
                "blocked_by" : new_owner_doc['requested_by'] } }})
            
            doc1 = tasks.find_one({"resource" : r_json , "requested_by" : new_owner_doc['requested_by'] , "requested_to" : s , "status" : "pending"})
            print(doc1['_id'])
            tasks.update_one({"_id" :  doc1['_id']} , {"$set": {"status" : "approved"}})

            bulk = tasks.initialize_unordered_bulk_op()
            bulk.find({"resource" : r_json , "requested_to" : s , "status" : "pending" , "requested_by" : {"$ne" : new_owner_doc['requested_by'] }}).update({ "$set": { "requested_to": new_owner_doc['requested_by']} })
            bulk.execute()
        else:
            resources.update_one({"r_name" : r_json} , {"$set" : {"status" : "available" , "slot_info" : {

                "start_time" : None,
                "end_time" : None,
                "blocked_by" : None } }})

       
    return jsonify({"status" : "released!"})
    

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)

