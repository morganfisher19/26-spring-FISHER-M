from flask import Flask, session, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

# Creates web server
app = Flask(__name__)

# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:data4001@localhost/congress_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
# api=Api(app)


# Define models
class MemberModel(db.Model):
    __tablename__='members'
    member_id=db.Column(db.String(8), primary_key=True)
    full_name=db.Column(db.Text)
    first_name=db.Column(db.Text)
    last_name=db.Column(db.Text)
    party=db.Column(db.String(1))
    chamber=db.Column(db.String(1))
    state_name=db.Column(db.Text)
    district=db.Column(db.Integer)
    years_in_congress=db.Column(db.Integer)
    age=db.Column(db.Integer)
    created_at=db.Column(db.DateTime(timezone=True))
    vote_records = db.relationship(
        'VoteRecordModel',
        backref='member',
        lazy=True
    )

class BillModel(db.Model):
    __tablename__='bills'
    bill_id=db.Column(db.Text, primary_key=True)
    bill_type=db.Column(db.Text)
    bill_num=db.Column(db.Integer)
    congress=db.Column(db.Integer)
    title=db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True))
    votes = db.relationship(
        'VoteModel',
        backref='bill',
        lazy=True
    )

    # Return value to represent data
    # def __repr__(self):
    #     return f"Bill: {self.title}"

# Will add amendment class when relevant
# class AmendmentModel(db.Model):
#     __tablename__='amendments'
#     amendment_id=db.Column(db.Text, primary_key=True)
#     amendment_type=db.Column(db.Text)
#     congress=db.Column(db.Integer)
#     purpose=db.Column(db.Text)
#     created_at=db.Column(db.DateTime(timezone=True))

class VoteModel(db.Model):
    __tablename__ = 'votes'
    vote_id=db.Column(db.String(15), primary_key=True)
    bill_id=db.Column(db.Text, db.ForeignKey('bills.bill_id'))
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
    bills = db.relationship(
        'BillModel',
        backref='bill',
        lazy=True
    )

class VoteRecordModel(db.Model):
    __tablename__ = 'vote_records'
    vote_id = db.Column(db.String(15), db.ForeignKey('votes.vote_id'), primary_key=True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key=True)
    position = db.Column(db.Text)
    # created_at=db.Column(db.DateTime(timezone=True))


# Create routes
@app.route('/')
def index():

    # Get all members to populate dropdown
    members = MemberModel.query.order_by(MemberModel.full_name).all()

    return render_template("index.html", members=members)


# Query members
@app.route('/member')
def get_member():
    full_name = request.args.get("full_name")

    member = MemberModel.query.filter_by(full_name=full_name).first()
    voteRecords=member.vote_records

    return render_template("member.html", member=member, voteRecords=voteRecords)




# Note: debug=False in production
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)
