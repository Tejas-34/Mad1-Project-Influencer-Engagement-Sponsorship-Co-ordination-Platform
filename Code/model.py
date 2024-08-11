from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), unique=True, nullable=False)
    Name = db.Column(db.String(80), unique=False, nullable=False)
    Username = db.Column(db.String(80), nullable=False)
    Password = db.Column(db.String(120), unique=False, nullable=False)
    Role = db.Column(db.String(80), unique=False, nullable=False)
    Bio = db.Column(db.String(150), unique=False, nullable=False)
    flagged = db.Column(db.Boolean, nullable=False, default=False)

    
    sponsor = db.relationship('Sponsor', backref='user', uselist=False,cascade='all, delete-orphan')
    influencer = db.relationship('Influencer', back_populates='user', uselist=False,lazy=True,cascade='all, delete-orphan')

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
    Budget = db.Column(db.Integer, unique=False, nullable=False)
    Industry = db.Column(db.String(80), unique=False, nullable=False)

    campaign = db.relationship('Campaign', backref='sponsor', lazy=True,cascade='all, delete-orphan')
    

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
    Category = db.Column(db.String(80), unique=False, nullable=False)
    Niche = db.Column(db.String(80), unique=False, nullable=False)
    Reach = db.Column(db.Integer, unique=False, nullable=False)


    adrequests = db.relationship('AdRequest', back_populates='influencer', lazy=True,cascade='all, delete-orphan')
    user = db.relationship('User', back_populates='influencer', uselist=False)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id',ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False, default='public')
    goals = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(80), nullable=True)
    flagged = db.Column(db.Boolean, nullable=False, default=False)

    
    adrequests = db.relationship('AdRequest', back_populates='campaign', lazy=True, cascade='all, delete-orphan')

    


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id',ondelete='CASCADE'), nullable=False)
    camp_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')
    messages = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.Boolean, nullable=False, default=False)
    

    influencer = db.relationship('Influencer', back_populates='adrequests')
    campaign = db.relationship('Campaign', back_populates='adrequests')
  

class InfluencerAdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id', ondelete='CASCADE'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id', ondelete='CASCADE'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')
    messages = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.Boolean, nullable=False, default=False)

    sponsor = db.relationship('Sponsor', backref=db.backref('influencer_ad_requests', cascade='all, delete-orphan', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('influencer_ad_requests', cascade='all, delete-orphan', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('influencer_ad_requests', cascade='all, delete-orphan', lazy=True))






