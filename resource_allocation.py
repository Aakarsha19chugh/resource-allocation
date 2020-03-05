from flask import Flask, render_template, url_for, request, session, redirect
import pymongo
import bcrypt
import json
from flask import jsonify
import datetime
from dateutil.parser import parse
from flask_admin import Admin

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://aakarshachug:aakarsha123@cluster0-qtf6n.mongodb.net/test?retryWrites=true&w=majority")
db = client.resource_allocation


@app.route('/')
def index():
    if 'username' in session:
        s = session['username']
        a = session['admin']
        if a == False:
            return render_template('index_dashboard.html' , name = s)
        else:
            return render_template('admin_dashboard.html' , name = s)

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
            session['admin'] = login_user['is_admin']
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
            print(document)
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

        if tasks.find({'resource' : r_json , 'requested_to' : s , 'status' : 'pending'}):
            y = tasks.find_one({"resource" : r_json, "status" : "pending" , "requested_to" : s})
            resources.update_one({'r_name' : r_json} ,{'$set' : {'slot_info' : 
            {'blocked_by' : y['requested_by'] , 'start_time' : datetime.datetime.now() , 'end_time' : y['end_time']  }}})
            
            doc1 = tasks.find_one({"resource" : r_json , "requested_by" : y['requested_by'] , "requested_to" : s , "status" : "pending"})
            tasks.update_one({"_id" :  doc1['_id']} , {"$set": {"status" : "approved"}})
            tasks.update_many({'resource' : r_json , 'requested_to' : s , 'status' : 'pending'}, {'$set' : {
                'requested_to' : y['requested_by']}})
            return ({"status" : 'released'})
                
        else:
            resources.update_one({"r_name" : r_json} , {"$set" : {"status" : "available" , "slot_info" : {

                "start_time" : None,
                "end_time" : None,
                "blocked_by" : None } }})
            return ({"status" : 'released'})



# Admin functions----------------------------------------------

@app.route('/addusername', methods=['POST'])
def addusername():
    if request.method == "POST":
        x = request.get_json()
        print(x)
        username = x['username']
        password = x['password']
        email = x['email']
        print(username , password , email)
        users = db.user_credentials
        existing_user = users.find_one({'username' : username})
        existing_email = users.find_one({'email' : email}) 
        
        if existing_user is None and existing_email is None:
            hashpass = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
            print(hashpass)
            users.insert({'username' : username, 'password' : hashpass , 'email' :email,
            "is_admin" : False
            
             })
        return jsonify({"status" : "User Added"})
        

@app.route('/displayusers', methods=['POST'])
def displayusers():
    if request.method == 'POST':
        users = db.user_credentials
        result = []
        for document in users.find({'is_admin' : False}):
            ans = {'username' : document['username'] , 'email' : document['email']}
            result.append(ans)
        
        print(result)
        return jsonify({'users' : result})

@app.route('/admintasks', methods=['POST'])
def admintasks():
    if request.method == 'POST':
        tasks = db.tasks
        result = []
        for document in tasks.find({"status" : "pending"}):
            ans = {'requested_by' : document['requested_by'] , 'requested_to' : document['requested_to'],
                 'resource' : document['resource'] , 'request_time' : document['request_time']
            
            }

            result.append(ans)
        
        print(result)
        return jsonify({'tasks' : result})

@app.route('/removeuser', methods=['POST'])
def removeuser():
    if request.method == 'POST':
        users = db.user_credentials
        tasks = db.tasks
        resources = db.resources
        
        # get username
        x = request.get_json()
        username = x['username']

        rown = []
        #check resources blocked by the user to be deleted
        for document in resources.find({'slot_info.blocked_by' : username}):
            rown.append(document['r_name'])
        
        for res in rown:
            #doc =  tasks.find({'requested_to' : username , 'status' : 'pending' , 'resource' : res})
            if tasks.count_documents({'requested_to' : username , 'status' : 'pending' , 'resource' : res}) > 0:
                
                new_owner = tasks.find_one({'requested_to' : username , 'status' : 'pending' , 'resource' : res})
                resources.update_one({'r_name' : res} , {'$set' : {'slot_info' : {

                    'blocked_by' : new_owner['requested_by'],
                    'start_time' : datetime.datetime.now(),
                    'end_time' : new_owner['end_time']  
                    }}})

                doc1 = tasks.find_one({"resource" : res , "requested_by" : new_owner['requested_by'] , "requested_to" : username , "status" : "pending"})
                tasks.update_one({"_id" :  doc1['_id']} , {"$set": {"status" : "approved"}})

                tasks.update_many({'resource' : res , 'requested_to' : username , 'status' : 'pending'}, {'$set' : {
                'requested_to' : new_owner['requested_by']}})
            
            else:
                resources.update_one({"r_name" : res} , {"$set" : {"status" : "available" , "slot_info" : {

                "start_time" : None,
                "end_time" : None,
                "blocked_by" : None } }})
        
        users.delete_one({'username' : username})
        
        return ({"status" : 'user removed!'})


@app.route('/addresource', methods=['POST'])
def addresource():
    if request.method == "POST":
        x = request.get_json()
        print(x)
        r_name = x['r_name']
        resources = db.resources
        existing_resource = resources.find_one({'r_name' : r_name})
        
        
        if existing_resource is None:
            resources.insert({'r_name' : r_name, 'status' : 'available', 'slot_info' : {
                'start_time' : None,
                'end_time' : None,
                'blocked_by' : None
                }
            
             })
        return jsonify({"status" : "Resource added"})


@app.route('/removeresource', methods=['POST'])
def removeresource():
    if request.method == 'POST':
        x = request.get_json()
        r_name = x['resource_name']
        resources = db.resources
        tasks = db.tasks

        resources.delete_one({"r_name" : r_name})
        tasks.delete_many({"resource" : r_name , 'status' : "pending"})
        
        return ({"status" : "resource deleted!"})


@app.route('/bookonbehalf', methods=['POST'])
def bookonbehalf():
    if request.method == "POST":
        x = request.get_json()
        status = x['status']
        if status == "available":
            resource = db.resources

            resource.update_one({'r_name' : x['resource_name']} , {'$set' : {'status' : 'booked' , 'slot_info' :{
                'start_time' : datetime.datetime.now(),
                'end_time' : x['new_end_time'],
                'blocked_by' : x['new_owner']


            }}})
        else:
            tasks = db.tasks
            tasks.insert_one({'requested_by' : x['new_owner'] , 'requested_to' : x['blocked_by'] , 'status' : 'pending',
        
            'resource' : x['resource_name'] , 'request_time' : datetime.datetime.now() , 'end_time' : x['new_end_time'] })

    return ({"status" : "resource booked!"})









if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)

