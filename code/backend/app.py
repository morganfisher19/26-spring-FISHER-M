from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import or_, and_, not_

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
    # created_at=db.Column(db.DateTime(timezone=True))
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
    laws = db.relationship(
        'LawModel',
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

class VotePartyTotalModel(db.Model):
    __tablename__ = 'vote_party_totals'
    vote_id = db.Column(db.String(20), db.ForeignKey('votes.vote_id'), primary_key=True)
    party = db.Column(db.String(1), primary_key=True)
    yes_count=db.Column(db.Integer)
    no_count=db.Column(db.Integer)
    present_count=db.Column(db.Integer)
    not_voting_count=db.Column(db.Integer)

class BillSponsorshipModel(db.Model):
    __tablename__='bill_sponsorships'
    bill_id=db.Column(db.String(20), db.ForeignKey('bills.bill_id'), primary_key=True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key=True)
    sponsor_type = db.Column(db.String(1), primary_key=True)

class LawModel(db.Model):
    __tablename__='laws'
    law_num=db.Column(db.Text, primary_key=True)
    law_type=db.Column(db.Text)
    bill_id=db.Column(db.String(20), db.ForeignKey('bills.bill_id'))
    law_date=db.Column(db.DateTime(timezone=True))
    congress=db.Column(db.Integer)
    chamber=db.Column(db.String(1))

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

# Keywords for filtering member votes
PASSAGE_KEYWORDS = [
    "Passage", "Pass", "Agreeing to the Resolution",
    "Joint Resolution", "Concurrent Resolution",
    "Concur in the Senate Amendment"
]

# Get individual member data for individual member pages
@app.route('/api/member/<string:member_id>')
def get_member(member_id):
    keyword_filters = or_(
        *[VoteModel.question.ilike(f'%{kw}%') for kw in PASSAGE_KEYWORDS]
    )

    procedural_filter = not_(and_(
        BillModel.bill_type == 'HRES',
        BillModel.title.ilike('providing for consideration%')
    ))

    m = (
        MemberModel.query
        .options(
            joinedload(MemberModel.vote_records)
            .joinedload(VoteRecordModel.vote)
            .joinedload(VoteModel.bill)
        )
        .filter_by(member_id=member_id)
        .first_or_404()
    )
    # m = MemberModel.query.filter_by(member_id=member_id).first()

    vote_records = (
        VoteRecordModel.query
        .join(VoteRecordModel.vote)
        .join(VoteModel.bill)
        .options(
            contains_eager(VoteRecordModel.vote)
            .contains_eager(VoteModel.bill)
            .joinedload(BillModel.laws)
        )
        .filter(VoteRecordModel.member_id == member_id)
        .filter(keyword_filters)
        .filter(procedural_filter)
        .all()
    )

    vote_data = []
    for vr in vote_records:
        vote = vr.vote
        bill = vote.bill
        vote_data.append({
            'vote_id': vr.vote_id,
            'vote_date': vote.vote_date.isoformat() if vote.vote_date else None,
            'bill_title': bill.title,
            'bill_type': bill.bill_type,
            'bill_num': bill.bill_num,
            'question': vote.question,
            'position': vr.position,
            'policy_area': bill.policy_area if bill else None,
            'became_law': len(bill.laws) > 0,
        })

    return jsonify({
        'member_id': m.member_id,
        'full_name': m.full_name,
        'party': m.party,
        'chamber': m.chamber,
        'state_name': m.state_name,
        'vote_records': vote_data
    })

@app.route('/api/member/<string:member_id>/sponsorships')
def get_member_sponsorships(member_id):
    sponsorships = (
        BillSponsorshipModel.query
        .join(BillSponsorshipModel.bill)
        .options(
            contains_eager(BillSponsorshipModel.bill)
            .joinedload(BillModel.laws)
        )
        .filter(BillSponsorshipModel.member_id == member_id)
        .all()
    )

    result = []
    for s in sponsorships:
        bill = s.bill
        result.append({
            'bill_id': s.bill_id,
            'sponsor_type': s.sponsor_type,
            'bill_title': bill.title if bill else None,
            'bill_type': bill.bill_type if bill else None,
            'bill_num': bill.bill_num if bill else None,
            'policy_area': bill.policy_area if bill else None,
            'became_law': len(bill.laws) > 0 if bill else False,
        })

    return jsonify(result)


# Data visualizations
@app.route('/api/visualizations/bipartisanship')
def get_bipartisanship():
    chamber = request.args.get("chamber")        # 'H' or 'S'
    party = request.args.get("party")            # 'D', 'R', 'I'
    policy_area = request.args.get("policy_area") # e.g. 'Health'
    
    PASSAGE_KEYWORDS = [
        "Passage", "Pass", "Agreeing to the Resolution",
        "Joint Resolution", "Concurrent Resolution",
        "Concur in the Senate Amendment"
    ]
    
    keyword_filters = or_(
        *[VoteModel.question.ilike(f'%{kw}%') for kw in PASSAGE_KEYWORDS]
    )

    procedural_filter = not_(and_(
        BillModel.bill_type == 'HRES',
        BillModel.title.ilike('providing for consideration%')
    ))

    query = (
        VoteModel.query
        .join(VoteModel.bill)
        .join(VoteModel.vote_party_totals)
        .options(
            contains_eager(VoteModel.vote_party_totals),
            contains_eager(VoteModel.bill)
        )
        .filter(keyword_filters)
        .filter(procedural_filter)
    )

    if chamber:
        query = query.filter(VoteModel.chamber == chamber)
    if policy_area:
        query = query.filter(BillModel.policy_area == policy_area)

    votes = query.order_by(VoteModel.vote_date).all()

    result = []
    for vote in votes:
        # Filter party totals if party param is provided
        party_totals = vote.vote_party_totals
        if party:
            party_totals = [pt for pt in party_totals if pt.party == party]

        result.append({
            'vote_id': vote.vote_id,
            'vote_date': vote.vote_date.isoformat() if vote.vote_date else None,
            'question': vote.question,
            'result': vote.result,
            'chamber': vote.chamber,
            'bill_id': vote.bill_id,
            'policy_area': vote.bill.policy_area if vote.bill else None,
            'party_totals': [
                {
                    'party': pt.party,
                    'yes_count': pt.yes_count,
                    'no_count': pt.no_count,
                    'present_count': pt.present_count,
                    'not_voting_count': pt.not_voting_count,
                    # Bipartisanship score: % of party that voted yes
                    'yes_pct': round(
                        pt.yes_count / (pt.yes_count + pt.no_count + pt.present_count)
                        if (pt.yes_count + pt.no_count + pt.present_count) > 0
                        else 0,
                        4
                    )
                }
                for pt in party_totals
            ]
        })

    return jsonify(result)
'''

A few things worth noting:

**The `yes_pct` field** — this is what you'll actually plot in D3. A bipartisanship metric you can derive from this is the difference in `yes_pct` between R and D on the same vote. Votes where both parties have high `yes_pct` are bipartisan; votes where one is high and one is low are partisan.

**The `party` filter** is applied in Python after the query rather than in SQL because you're already eager-loading all party totals per vote — filtering in SQL there would break the eager load and you'd lose the other parties' data for cross-party comparison. If you only ever need one party, move it to SQL.

**Example URLs your frontend will call:**
```
/api/visualizations/bipartisanship
/api/visualizations/bipartisanship?chamber=H
/api/visualizations/bipartisanship?chamber=S&policy_area=Health

Second route:
@app.route('/api/bills/policy-areas')
def get_policy_areas():
    areas = (
        db.session.query(BillModel.policy_area)
        .filter(BillModel.policy_area.isnot(None))
        .distinct()
        .order_by(BillModel.policy_area)
        .all()
    )
    return jsonify([a[0] for a in areas])

'''

if __name__ == '__main__':
    # Note: debug=False in production
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8000, debug=True)
