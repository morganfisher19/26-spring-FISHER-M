from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import or_, and_, not_
from sqlalchemy import func, case, distinct

# Connect to frontend

DB_PASSWORD = os.getenv("DB_PASSWORD")

# Creates web server
app = Flask(__name__)

CORS(app)

# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{DB_PASSWORD}@localhost/congress_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class MemberModel(db.Model):
    __tablename__ = 'members'
    member_id = db.Column(db.String(8), primary_key = True)
    full_name = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    party = db.Column(db.String(1))
    chamber = db.Column(db.String(1))
    state_name = db.Column(db.String(2))
    district = db.Column(db.Integer)
    years_in_congress = db.Column(db.Integer)
    age = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime(timezone = True))
    vote_records = db.relationship(
        'VoteRecordModel',
        backref = 'member',
        lazy = True
    )
    bill_sponsorships = db.relationship(
        'BillSponsorshipModel',
        backref = 'member',
        lazy = True
    )

class BillModel(db.Model):
    __tablename__ = 'bills'
    bill_id = db.Column(db.String(20), primary_key = True)
    bill_type = db.Column(db.Text)
    bill_num = db.Column(db.Integer)
    congress = db.Column(db.Integer)
    chamber = db.Column(db.String(1))
    title = db.Column(db.Text)
    policy_area = db.Column(db.Text)
    votes = db.relationship(
        'VoteModel',
        backref = 'bill',
        lazy = True
    )
    bill_sponsorships = db.relationship(
        'BillSponsorshipModel',
        backref = 'bill',
        lazy = True
    )
    laws = db.relationship(
        'LawModel',
        backref = 'bill',
        lazy = True
    )

class VoteModel(db.Model):
    __tablename__ = 'votes'
    vote_id = db.Column(db.String(20), primary_key = True)
    bill_id = db.Column(db.String(20), db.ForeignKey('bills.bill_id'))
    question = db.Column(db.Text)
    chamber = db.Column(db.String(1))
    congress = db.Column(db.Integer)
    session_num = db.Column(db.Integer)
    vote_date = db.Column(db.DateTime(timezone = True))
    result = db.Column(db.Text)
    vote_records = db.relationship(
        'VoteRecordModel',
        backref = 'vote',
        lazy = True
    )
    vote_party_totals = db.relationship(
        'VotePartyTotalModel',
        backref = 'vote',
        lazy = True
    )

class VoteRecordModel(db.Model):
    __tablename__ = 'vote_records'
    vote_id = db.Column(db.String(20), db.ForeignKey('votes.vote_id'), primary_key = True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key = True)
    position = db.Column(db.Text)

class VotePartyTotalModel(db.Model):
    __tablename__ = 'vote_party_totals'
    vote_id = db.Column(db.String(20), db.ForeignKey('votes.vote_id'), primary_key = True)
    party = db.Column(db.String(1), primary_key = True)
    yes_count = db.Column(db.Integer)
    no_count = db.Column(db.Integer)
    present_count = db.Column(db.Integer)
    not_voting_count = db.Column(db.Integer)

class BillSponsorshipModel(db.Model):
    __tablename__ = 'bill_sponsorships'
    bill_id = db.Column(db.String(20), db.ForeignKey('bills.bill_id'), primary_key = True)
    member_id = db.Column(db.String(8), db.ForeignKey('members.member_id'), primary_key = True)
    sponsor_type = db.Column(db.String(1), primary_key = True)

class LawModel(db.Model):
    __tablename__ = 'laws'
    law_num = db.Column(db.Text, primary_key = True)
    law_type = db.Column(db.Text)
    bill_id = db.Column(db.String(20), db.ForeignKey('bills.bill_id'))
    law_date = db.Column(db.DateTime(timezone = True))
    congress = db.Column(db.Integer)
    chamber = db.Column(db.String(1))

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
        'full_name' : m.full_name,
        'first_name': m.first_name,
        'last_name': m.last_name,
        'party': m.party,
        'chamber': m.chamber,
        'state_name': m.state_name,
        'district': m.district
    } for m in members])

# Keywords for filtering member votes
PASSAGE_KEYWORDS = [
    "Passage", "Pass", "Agreeing to the Resolution",
    "Joint Resolution", "Concurrent Resolution",
    "Concur in the Senate Amendment"
]

# Get individual member voting data for individual member pages
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
        .filter_by(member_id = member_id)
        .first_or_404()
    )
    # m = MemberModel.query.filter_by(member_id = member_id).first()

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

# Get individual member sponsorship data
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

# BIPARTISANSHIP WITHIN CONGRESS
@app.route('/api/visualizations/bipartisanship')
def get_bipartisanship():
    chamber = request.args.get("chamber")        # 'H' or 'S'
    party = request.args.get("party")            # 'D', 'R', 'I'
    policy_area = request.args.get("policy_area") # e.g. 'Health'
    
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
        query = query.filter(BillModel.policy_area ==  policy_area)

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

# ─────────────────────────────────────────────
# 2) HOW A BILL SURVIVES CONGRESS
# Funnel: introduced → voted on → passed one chamber
#         → passed both chambers → became law
# ─────────────────────────────────────────────
@app.route('/api/visualizations/bill_funnel')
def get_bill_funnel():

    # Total bills introduced
    total_introduced = BillModel.query.count()

    # Bills that have at least one vote
    voted_on = (
        db.session.query(func.count(distinct(VoteModel.bill_id)))
        .filter(VoteModel.bill_id.isnot(None))
        .scalar()
    )

    # Bills that passed at least one chamber
    # A bill "passed" a chamber if any vote on it has a passing result
    PASS_RESULTS = ["Passed", "Agreed to"]
    pass_result_filter = or_(*[VoteModel.result.ilike(f'%{r}%') for r in PASS_RESULTS])

    passed_one = (
        db.session.query(func.count(distinct(VoteModel.bill_id)))
        .filter(pass_result_filter)
        .scalar()
    )

    # Bills that passed both chambers:
    # bill_id appears in passing votes from BOTH 'H' and 'S'
    h_passed = (
        db.session.query(VoteModel.bill_id)
        .filter(pass_result_filter, VoteModel.chamber == 'H')
        .distinct()
        .subquery()
    )
    s_passed = (
        db.session.query(VoteModel.bill_id)
        .filter(pass_result_filter, VoteModel.chamber == 'S')
        .distinct()
        .subquery()
    )
    passed_both = (
        db.session.query(func.count())
        .select_from(h_passed)
        .join(s_passed, h_passed.c.bill_id == s_passed.c.bill_id)
        .scalar()
    )

    # Bills that became law
    became_law = db.session.query(func.count(distinct(LawModel.bill_id))).scalar()

    return jsonify({
        'stages': [
            {'label': 'Introduced',         'count': total_introduced},
            {'label': 'Voted On',           'count': voted_on},
            {'label': 'Passed One Chamber', 'count': passed_one},
            {'label': 'Passed Both',        'count': passed_both},
            {'label': 'Became Law',         'count': became_law},
        ]
    })


# ─────────────────────────────────────────────
# 3) CONGRESSIONAL ACTIVITY OVER TIME
# Query params:
#   chamber     — 'H' | 'S'               (optional)
#   granularity — 'day' | 'week' | 'month' (default: week)
#   policy_area — e.g. 'Health'            (optional)
# ─────────────────────────────────────────────
@app.route('/api/visualizations/activity_over_time')
def get_activity_over_time():
    chamber     = request.args.get('chamber')
    granularity = request.args.get('granularity', 'week')
    policy_area = request.args.get('policy_area')

    # Date truncation based on granularity
    trunc_map = {
        'day':   'day',
        'week':  'week',
        'month': 'month',
    }
    trunc = trunc_map.get(granularity, 'week')
    period = func.date_trunc(trunc, VoteModel.vote_date)

    query = (
        db.session.query(
            period.label('period'),
            func.count(VoteModel.vote_id).label('vote_count')
        )
        .join(VoteModel.bill)
        .filter(VoteModel.vote_date.isnot(None))
    )

    if chamber:
        query = query.filter(VoteModel.chamber == chamber)
    if policy_area:
        query = query.filter(BillModel.policy_area == policy_area)

    rows = (
        query
        .group_by(period)
        .order_by(period)
        .all()
    )

    return jsonify({
        'granularity': granularity,
        'data': [
            {
                'period':     r.period.isoformat() if r.period else None,
                'vote_count': r.vote_count
            }
            for r in rows
        ]
    })


# ─────────────────────────────────────────────
# 4) TOP INFLUENCERS IN CONGRESS
# Query params:
#   metric      — 'laws' | 'sponsored' | 'cosponsors' (default: laws)
#   chamber     — 'H' | 'S'                            (optional)
#   party       — 'D' | 'R' | 'I'                      (optional)
#   policy_area — e.g. 'Health'                         (optional)
#   limit       — int, default 10
# ─────────────────────────────────────────────
@app.route('/api/visualizations/top_influencers')
def get_top_influencers():
    metric      = request.args.get('metric', 'laws')
    chamber     = request.args.get('chamber')
    party       = request.args.get('party')
    policy_area = request.args.get('policy_area')
    limit       = int(request.args.get('limit', 10))

    # Base member filters (shared across all metrics)
    def apply_member_filters(q):
        if chamber:
            q = q.filter(MemberModel.chamber == chamber)
        if party:
            q = q.filter(MemberModel.party == party)
        return q

    if metric == 'laws':
        # Members ranked by number of distinct bills they sponsored that became law
        q = (
            db.session.query(
                MemberModel.member_id,
                MemberModel.full_name,
                MemberModel.party,
                MemberModel.chamber,
                MemberModel.state_name,
                func.count(distinct(LawModel.law_num)).label('score')
            )
            .join(BillSponsorshipModel, MemberModel.member_id == BillSponsorshipModel.member_id)
            .join(BillModel, BillSponsorshipModel.bill_id == BillModel.bill_id)
            .join(LawModel, BillModel.bill_id == LawModel.bill_id)
            .filter(BillSponsorshipModel.sponsor_type == 'S')  # primary sponsors only
        )
        if policy_area:
            q = q.filter(BillModel.policy_area == policy_area)
        q = apply_member_filters(q)
        q = q.group_by(
            MemberModel.member_id,
            MemberModel.full_name,
            MemberModel.party,
            MemberModel.chamber,
            MemberModel.state_name
        ).order_by(func.count(distinct(LawModel.law_num)).desc()).limit(limit)

    elif metric == 'sponsored':
        # Members ranked by number of bills sponsored
        q = (
            db.session.query(
                MemberModel.member_id,
                MemberModel.full_name,
                MemberModel.party,
                MemberModel.chamber,
                MemberModel.state_name,
                func.count(distinct(BillSponsorshipModel.bill_id)).label('score')
            )
            .join(BillSponsorshipModel, MemberModel.member_id == BillSponsorshipModel.member_id)
            .join(BillModel, BillSponsorshipModel.bill_id == BillModel.bill_id)
            .filter(BillSponsorshipModel.sponsor_type == 'S')
        )
        if policy_area:
            q = q.filter(BillModel.policy_area == policy_area)
        q = apply_member_filters(q)
        q = q.group_by(
            MemberModel.member_id,
            MemberModel.full_name,
            MemberModel.party,
            MemberModel.chamber,
            MemberModel.state_name
        ).order_by(func.count(distinct(BillSponsorshipModel.bill_id)).desc()).limit(limit)

    elif metric == 'cosponsors':
        # Members ranked by number of cosponsors their sponsored bills attracted
        cosponsor_count = (
            db.session.query(
                BillSponsorshipModel.bill_id,
                func.count(BillSponsorshipModel.member_id).label('n')
            )
            .filter(BillSponsorshipModel.sponsor_type == 'C')
            .group_by(BillSponsorshipModel.bill_id)
            .subquery()
        )
        q = (
            db.session.query(
                MemberModel.member_id,
                MemberModel.full_name,
                MemberModel.party,
                MemberModel.chamber,
                MemberModel.state_name,
                func.coalesce(func.sum(cosponsor_count.c.n), 0).label('score')
            )
            .join(BillSponsorshipModel, MemberModel.member_id == BillSponsorshipModel.member_id)
            .join(BillModel, BillSponsorshipModel.bill_id == BillModel.bill_id)
            .outerjoin(cosponsor_count, BillModel.bill_id == cosponsor_count.c.bill_id)
            .filter(BillSponsorshipModel.sponsor_type == 'S')
        )
        if policy_area:
            q = q.filter(BillModel.policy_area == policy_area)
        q = apply_member_filters(q)
        q = q.group_by(
            MemberModel.member_id,
            MemberModel.full_name,
            MemberModel.party,
            MemberModel.chamber,
            MemberModel.state_name
        ).order_by(func.coalesce(func.sum(cosponsor_count.c.n), 0).desc()).limit(limit)

    else:
        return jsonify({'error': f'Unknown metric: {metric}'}), 400

    rows = q.all()

    return jsonify({
        'metric': metric,
        'data': [
            {
                'member_id':  r.member_id,
                'full_name':  r.full_name,
                'party':      r.party,
                'chamber':    r.chamber,
                'state_name': r.state_name,
                'score':      r.score,
            }
            for r in rows
        ]
    })


# ─────────────────────────────────────────────
# HELPER: distinct policy areas (useful for filter dropdowns)
# ─────────────────────────────────────────────
@app.route('/api/policy_areas')
def get_policy_areas():
    rows = (
        db.session.query(BillModel.policy_area)
        .filter(BillModel.policy_area.isnot(None))
        .distinct()
        .order_by(BillModel.policy_area)
        .all()
    )
    return jsonify([r.policy_area for r in rows])

if __name__ == '__main__':
    # Note: debug = False in production
    app.run(debug = True)
    # app.run(host = '0.0.0.0', port = 8000, debug = True)
