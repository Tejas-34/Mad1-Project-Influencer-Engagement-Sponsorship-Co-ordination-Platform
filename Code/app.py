from flask import Flask,render_template,redirect,url_for,request,session
from model import db,User,Sponsor,Influencer, Campaign,AdRequest,InfluencerAdRequest
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import uuid



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ISPC.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'asnkfjnsajcajdsckj'


db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')



#-----------------------login page for user-------------------
@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        c = User.query.filter_by(Username=username,Password=password).first()
        if c and not(c.flagged):
            if c.Role == 'sponsor':
                
                return redirect(url_for('dashboard_spo',id=c.id))
            else:
                return redirect(url_for('dashboard_inf',id=c.id))
        else:
            return render_template('user-login.html', error='Invalid username or password')
    else:
        return render_template('user-login.html')




#------------------sign in page for Influencer-----------------
@app.route('/influencer', methods=['GET', 'POST'])
def influencer():
    if request.method == 'POST':
        Name = request.form['Name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        Bio = request.form['Bio']
        role = 'influencer'
        category = request.form['Category']
        niche = request.form['Niche']
        reach = request.form['Reach']


        bymail = User.query.filter_by(Email = email).first()
        byusername = User.query.filter_by(Username=username).first()
        
        if(bymail == None and byusername==None):
            user = User(Email=email,Name=Name, Username=username, Password=password, Bio=Bio,Role=role,flagged=False )
            db.session.add(user)
            db.session.commit()

            influencer = Influencer( Category=category, Niche=niche, Reach=reach,user_id = user.id)
            db.session.add(influencer)
            db.session.commit()
             # Redirect to a thank you or success page
            return redirect(url_for('thank_you'))
        else:
            return render_template('inf_signup.html',error="Username or Email already exits") 
    return render_template('inf_signup.html')


#--------------------------------dashboard for influencer-----------------------------
@app.route('/dashboard-inf/<int:id>', methods=['GET', 'POST'])
def dashboard_inf(id):
    if request.method == 'GET':
        user = User.query.filter_by(id=id).first()
        req = AdRequest.query.filter_by(influencer_id=user.influencer.id).all()
        req1 = InfluencerAdRequest.query.filter_by(influencer_id=user.influencer.id).all()
        
        if user:
            return render_template('Dashboard-influencer.html', user=user,request=(req+req1))
        else:
            return f'''<p>User with id {id} does not exist.</p>'''
    return render_template('dashboard.html')


#update profile for influencer
@app.route('/inf_update/<int:id>', methods=['GET', 'POST'])
def inf_update(id):
    if request.method == 'GET':
        user = User.query.filter_by(id=id).first()
        return render_template('inf_update.html', user=user)
    
    if request.method == 'POST':
        user = User.query.filter_by(id=id).first()
        user.Name = request.form['Name']
        user.Email = request.form['Email']
        user.Username = request.form['Username']
        user.Password = request.form['Password']
        user.Bio = request.form['Bio']
        user.influencer.Category = request.form['Category']
        user.influencer.Niche = request.form['Niche']
        user.influencer.Reach = request.form['Reach']
        db.session.commit()
        return redirect(url_for('dashboard_inf', id=user.id))
        



#add request page for influencer
@app.route('/add_req/<int:id>', methods=['GET', 'POST'])
def add_req(id):
    user = User.query.filter_by(id=id).first()
    inf = Influencer.query.filter_by(user_id=user.id).first()
    if request.method == 'GET':
        req = AdRequest.query.filter_by(influencer_id=inf.id).all()
        #Camp = Campaign.query.filter_by(id=req.campaign_id).all()
        return render_template('adrequest.html', adrequest=req,user=user)
        

@app.route('/accept_ad_request/<int:ad_request_id>/<int:id>', methods=['POST'])
def accept_ad_request(ad_request_id,id):
    ad_request = AdRequest.query.get(ad_request_id)
    if ad_request:
        ad_request.status = 'Accepted'
        db.session.commit()
    return redirect(url_for('add_req', id=id))


#reject request for influencer
@app.route('/reject_ad_request/<int:ad_request_id>/<int:id>', methods=['POST'])
def reject_ad_request(ad_request_id,id):
    ad_request = AdRequest.query.get(ad_request_id)
    if ad_request:
        if ad_request.status == 'Rejected':
            #using adrequest id
            req = AdRequest.query.filter_by(id=ad_request_id).first()
            db.session.delete(req)
            db.session.commit()
        ad_request.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('add_req', id=id))




#edit ad request route
@app.route('/edit_adreq/<int:id>/<int:user_id>',methods=['POST'])
def edit_adreq(id,user_id):
    user = User.query.get(user_id)
    req = AdRequest.query.get(id)
    req.payment_amount = request.form['payment']
    req.messages = request.form['Message']
    req.requirements = request.form['Req']
    db.session.commit()
    return redirect(url_for('my_campaigns', id=user.id))


#delete ad request from sponsor
@app.route('/delete_adreq/<int:id>/<int:user_id>')
def delete_adreq(id,user_id):
    user = User.query.get(user_id)
    req = AdRequest.query.filter_by(id=id).first()
    db.session.delete(req)
    db.session.commit()   
    return redirect(url_for('my_campaigns', id=user.id))


#search campaing
@app.route('/search_camp/<int:id>',methods=['GET','POST'])
def search_camp(id):
    user = User.query.get(id)
    if request.method == 'POST':
        name = request.form.get('name').lower()
        category = request.form.get('search').lower()
        query = Campaign.query.filter((Campaign.name.ilike(f'%{name}%')) & (Campaign.category.ilike(f'%{category}%')) & (Campaign.visibility == 'public'))
        search_results = query.all()
        print(name,category,search_results)
        return render_template('search_campage.html', public_campaigns=search_results,user=user)
    return render_template('search_campage.html',user=user)



#send request to sponsor for particular campaign
@app.route('/send_request/<int:id>/<int:camp_id>/<int:spo_id>', methods=['GET', 'POST'])
def send_request(id,camp_id,spo_id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        status = 'Pending'
        message = request.form['message']
        req = InfluencerAdRequest(sponsor_id=spo_id, influencer_id=user.influencer.id, campaign_id=camp_id, messages=message, status=status, flagged=False)
        db.session.add(req)
        db.session.commit()
        return redirect(url_for('search_camp', id=user.id))
    return render_template('search_campage.html', user=user)



#check request sponsor
@app.route('/spo_request/<int:id>')
def spo_request(id):
    user = User.query.filter_by(id=id).first()
    spoid= user.sponsor.id
    query = InfluencerAdRequest.query.filter_by(sponsor_id=spoid)
    total = query.count()
    req = query.all()
    return render_template('spo_request.html',requests=req,user=user,total=total)
    
#accept request sponsor
@app.route('/sponsor/accept/<int:id>/<int:user_id>', methods=['GET', 'POST'])
def accept_req(id,user_id):
    req = InfluencerAdRequest.query.filter_by(id=id).first()
    req.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('spo_request',id=user_id))


#reject request sponsor
@app.route('/sponsor/reject/<int:id>/<int:user_id>', methods=['GET', 'POST'])
def reject_req(id,user_id):
    req = InfluencerAdRequest.query.filter_by(id=id).first()
    req.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('spo_request',id=user_id))


#log out for influencer
@app.route('/logout/<int:id>', methods=['GET', 'POST'])
def logout(id):
    return redirect(url_for('index'))




#-------------------------------------------------------- Spnsor Routes ------------------------------------

#sign in page for Sponsor
@app.route('/sponsor', methods=['GET', 'POST'])
def sponsor():
    if request.method == 'POST':
        Name = request.form['Name']
        Industry = request.form['Industry']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        Budget = request.form['Budget']
        Bio = request.form['Bio']
        role = 'sponsor'
        
        bymail =User.query.filter_by(Email=email).first()
        byusername =  User.query.filter_by(Username=username).first()

        if(bymail == None and byusername == None):
            user = User(Email=email,Name=Name, Username=username, Password=password, Bio=Bio,Role=role,flagged=False)
            db.session.add(user)
            db.session.commit()

            sponsor = Sponsor( Industry=Industry, Budget=Budget, user_id = user.id)
            db.session.add(sponsor)
            db.session.commit()
            # Redirect to a thank you or success page
            return redirect(url_for('thank_you'))
            
            
        else:
            return render_template('spo_signup.html',error="Username or Email already exits")
            
            

    # For GET requests, render the registration form
    return render_template('spo_signup.html')



#crearte campainge sponsor
@app.route('/create_camp/<int:id>', methods=['GET', 'POST'])
def create_camp(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        # Campaign.__table__.drop(db.engine)
        
        Name = request.form['Name']
        Description = request.form['Description']
        Start_date = request.form['Start_date']
        End_date = request.form['End_date']
        Budget = request.form['Budget']
        goals = request.form['goal']
        category = request.form['category']
        visibility = request.form['visibility']
        Start_date = datetime.strptime(Start_date, '%Y-%m-%d')
        End_date = datetime.strptime(End_date, '%Y-%m-%d')

        camp = Campaign(name=Name, description=Description, start_date=Start_date,category=category, end_date=End_date, budget=Budget, goals=goals,visibility=visibility, sponsor_id=user.sponsor.id, flagged=False)
        db.session.add(camp)
        db.session.commit()
        # Redirect to a my campaigns page
        return redirect(url_for('my_campaigns', id=user.id))
    return render_template('create_camp.html',user=user)

#update campaign sponsor
@app.route('/update_camp/<int:id>/<int:user_id>', methods=['POST'])
def update_camp(id,user_id):
    camp = Campaign.query.filter_by(id=id).first()
    if request.method == 'POST':
        camp.name = request.form['Name']
        camp.description = request.form['description']
        camp.start_date = datetime.strptime(request.form['Start_date'],'%Y-%m-%d')
        camp.end_date = datetime.strptime(request.form['end_date'],'%Y-%m-%d')
        camp.budget = request.form['Budget']
        camp.goals = request.form['goals']
        camp.category = request.form['category']
        camp.visibility = request.form['visibility']
        db.session.commit()
        return redirect(url_for('my_campaigns',id=user_id))
    


  


#search influencer for sponsor
@app.route('/search_inf/<int:id>', methods=['GET', 'POST'])
def search_inf(id):
    user = User.query.filter_by(id=id).first()
    Campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.id).all()
    if request.method == 'POST':
        name = request.form.get('Name').lower()
        category = request.form.get('Category').lower()
        query = db.session.query(Influencer).join(User).filter(User.Role == 'influencer')
        print(query)
        query = query.filter((User.Name.ilike(f'%{name}%')) & (Influencer.Category.ilike(f'%{category}%')))
        search_results = query.all()
        return render_template('search_inf.html', search_results=search_results, user=user,Campaigns=Campaigns)
    return render_template('search_inf.html',user=user, Campaigns=Campaigns)




#---------------------------------------- send request to influencer -----------------------------------------


@app.route('/send_req/<int:id>/<int:inf_id>', methods=['GET', 'POST'])
def send_req(id,inf_id):
    user = User.query.filter_by(id=id).first()
    inf = Influencer.query.filter_by(user_id=inf_id).first()
    # AdRequest.__table__.drop(db.engine)
    if request.method == 'POST':
        
        campaign_id = request.form['campaign_id']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        status = 'Pending'
        message = request.form['message']
        req = AdRequest(camp_id=campaign_id, influencer_id=inf.id, requirements=requirements, payment_amount=payment_amount, messages=message, status=status, flagged=False)
        db.session.add(req)
        db.session.commit()

        return redirect(url_for('search_inf', id=user.id))
    return render_template('search_inf.html', user=user)




@app.route('/my_campaigns/<int:id>', methods=['GET', 'POST'])
def my_campaigns(id):
    user = User.query.filter_by(id=id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.id).all()
    return render_template('my_campaigns.html', campaigns=campaigns, user=user)


@app.route('/del_camp/<int:id>/<int:user>', methods=['GET', 'POST'])
def del_camp(id,user):
    camp = Campaign.query.filter_by(id=id).first()
    db.session.delete(camp)
    db.session.commit()
    return redirect(url_for('my_campaigns', id=user))



#registration tank you route
@app.route('/thank_you')
def thank_you():
    return f'''<h3 style="color:red;"> Thank you for registering! </h3>
                <p> Your registration is complete. </p>
                <a href="/user">Return to the login page</a>
            '''


#dashboard for sponsor
@app.route('/dashboard-spo/<int:id>', methods=['GET', 'POST']) 
def dashboard_spo(id):
    if request.method == 'GET':
        user = User.query.filter_by(id=id).first()
        if user:
            return render_template('Dashboard-sponsor.html', user=user)
        else:
            return f'''<p>User with id {id} does not exist.</p>'''
    return render_template('dashboard.html')



#update profile for sponsor
@app.route('/user/spo_update/<int:id>', methods=['GET', 'POST'])
def spo_update(id):
    if request.method == 'GET':
        user = User.query.filter_by(id=id).first()
        return render_template('spo_update.html', user=user)
    
    if request.method == 'POST':
        user = User.query.filter_by(id=id).first()
        user.Name = request.form['Name']
        user.Email = request.form['Email']
        user.Username = request.form['Username']
        user.Password = request.form['Password']
        user.Bio = request.form['Bio']
        user.sponsor.Industry = request.form['Industry']
        user.sponsor.Budget = request.form['Budget']
        db.session.commit()
        return redirect(url_for('dashboard_spo', id=user.id))




#----------------------------- Admin Routes ---------------------------------


#login page for admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == '123':
            return redirect(url_for('admin_dashboard'))
    return render_template('adm_login.html')



#dashboard for admin
@app.route('/admin/dashboard')
def admin_dashboard():
    total_users = int(User.query.count())
    total_sponsor = int(Sponsor.query.count())
    total_inf = int(Influencer.query.count())
    flagged_users = int(User.query.filter_by(flagged=True).count())
    total_campaigns = int(Campaign.query.count())
    flagged_campaigns = int(Campaign.query.filter_by(flagged=True).count())
    
    print(total_campaigns,total_users,total_inf,flagged_users,flagged_campaigns)


    #---------------------Total V Flagged Graphs -------------------------------
    try:
        categories = ['Users', 'Campaigns']
        total_values = [total_users,total_campaigns]
        flagged_values = [flagged_users, flagged_campaigns]
        plt.clf()
        x = range(len(categories))
        fig, ax = plt.subplots()
        
        # Total values
        ax.bar(x, total_values, width=0.4, label='Total', align='center')
        # Flagged values
        ax.bar(x, flagged_values, width=0.4, label='Flagged', align='edge',color='red')

        ax.set_xlabel('Categories')
        ax.set_ylabel('Counts')
        ax.set_title('Total vs Flagged Counts')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        filename = f"static/{uuid.uuid4()}.png"
        plt.savefig(filename)
        plt.close()


        labels = ['Sponsors', 'Influencers']
        values = [total_sponsor, total_inf]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribution of Users')
        filename2 = f"static/{uuid.uuid4()}.png"
        plt.savefig(filename2)
        plt.close()
        return render_template('Dashboard-Admin.html', file1 = filename, file2 = filename2)
    except:
        return render_template('Dashboard-Admin.html')  



#--------------------------------------------- Manage Users ----------------------------------------

@app.route('/admin/users')
def manage_users():
    users = User.query.all()
    total = User.query.count()
    return render_template('adm-manage_user.html', users=users,total=total)



@app.route('/admin/users/flag/<int:id>', methods=['POST', 'GET'])
def flag_user(id):
    user = User.query.filter_by(id=id).first()
    if user.flagged:
        user.flagged=False
    else:
        user.flagged = True
    db.session.commit()
    return redirect(url_for('manage_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['GET','POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage_users'))

@app.route('/admin/users/update/<int:id>', methods=['POST'])
def update(id):
    user = User.query.get(id)
    if(request.method == 'POST'):
        user.Name = request.form['name']
        user.Username = request.form['username']
        user.Password= request.form['password']
        user.Email = request.form['email']
        db.session.commit()
        return redirect(url_for('manage_users'))


@app.route('/admin/logout')
def adm_log():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
