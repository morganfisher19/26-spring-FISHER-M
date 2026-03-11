from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

# Connect to frontend

DB_PASSWORD = os.getenv("DB_PASSWORD")

# Creates web server
app = Flask(__name__)

CORS(app)

# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI']=f'postgresql://postgres:{DB_PASSWORD}@localhost/congress_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

# Define models
class MemberModel(db.Model):
    __tablename__='members'
    member_id=db.Column(db.String(8), primary_key=True)
    full_name=db.Column(db.Text)
    first_name=db.Column(db.Text)
    last_name=db.Column(db.Text)
    party=db.Column(db.String(1))
    chamber=db.Column(db.String(1))
    state_name=db.Column(db.String(2))
    district=db.Column(db.Integer)
    years_in_congress=db.Column(db.Integer)
    age=db.Column(db.Integer)
    created_at=db.Column(db.DateTime(timezone=True))
    vote_records = db.relationship(
        'VoteRecordModel',
        backref='member',
        lazy=True
    )
    bill_sponsorships = db.relationship(
        'BillSponsorshipModel',
        backref='member',
        lazy=True
    )

class BillModel(db.Model):
    __tablename__='bills'
    bill_id=db.Column(db.String(20), primary_key=True)
    bill_type=db.Column(db.Text)
    bill_num=db.Column(db.Integer)
    congress=db.Column(db.Integer)
    chamber=db.Column(db.String(1))
    title=db.Column(db.Text)
    policy_area=db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True))
    votes = db.relationship(
        'VoteModel',
        backref='bill',
        lazy=True
    )
    bill_sponsorships = db.relationship(
        'BillSponsorshipModel',
        backref='bill',
        lazy=True
    )

class VoteModel(db.Model):
    __tablename__ = 'votes'
    vote_id=db.Column(db.String(20), primary_key=True)
    bill_id=db.Column(db.String(20), db.ForeignKey('bills.bill_id'))
    question=db.Column(db.Text)
    chamber=db.Column(db.String(1))
    congress=db.Column(db.Integer)
    session_num=db.Column(db.Integer)
    vote_date=db.Column(db.DateTime(timezone=True))
    result=db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True))
    vote_records = db.relationship(
        'VoteRecordModel',
        backref='vote',
        lazy=True
    )
    vote_party_totals = db.relationship(
        'VotePartyTotalModel',
        backref='vote',
        lazy=True
    )

class VoteRecordModel(db.Model):
    __tablename__ = 'vote_records'
    vote_id = db.Column(db.String(20), db.ForeignKey('votes.vote_id'), primary_key=True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key=True)
    position = db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True))

class VotePartyTotalModel(db.Model):
    __tablename__ = 'vote_party_totals'
    vote_id = db.Column(db.String(20), db.ForeignKey('votes.vote_id'), primary_key=True)
    party = db.Column(db.String(1), primary_key=True)
    yes_count=db.Column(db.Integer)
    no_count=db.Column(db.Integer)
    present_count=db.Column(db.Integer)
    not_voting_count=db.Column(db.Integer)
    created_at=db.Column(db.DateTime(timezone=True))

class BillSponsorshipModel(db.Model):
    __tablename__='bill_sponsorships'
    bill_id=db.Column(db.String(20), db.ForeignKey('bills.bill_id'), primary_key=True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key=True)
    sponsor_type = db.Column(db.String(1), primary_key=True)
    created_at=db.Column(db.DateTime(timezone=True))

# To check API is working:
@app.route('/api/health')
def health():
    return {'status': 'ok'}

# Get member data for home page member search
@app.route('/api/members')
def get_members():
    members = MemberModel.query.order_by(MemberModel.full_name).all()
    return jsonify([{
        'member_id': m.member_id,
        'full_name': m.full_name
    } for m in members])


# Get individual member data for individual member pages
@app.route('/api/member/<string:member_id>')
def get_member(member_id):
    m = MemberModel.query.filter_by(member_id=member_id).first_or_404()
    return jsonify({
        'member_id': m.member_id,
        'full_name': m.full_name,
        'party': m.party,
        'chamber': m.chamber,
        'state_name': m.state_name,
        'vote_records': [{'vote_id': vr.vote_id, 'position': vr.position} for vr in m.vote_records]
    })



if __name__ == '__main__':
    # Note: debug=False in production
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)
