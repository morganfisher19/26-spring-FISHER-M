from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import or_, and_, not_, func, distinct
import os


# CONNECT TO DATABASE
DB_PASSWORD = os.getenv("DB_PASSWORD")

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{DB_PASSWORD}@localhost/congress_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS
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

# FILTER HELPERS
PASSAGE_KEYWORDS = [
    "Passage", "Pass", "Agreeing to the Resolution",
    "Joint Resolution", "Concurrent Resolution",
    "Concur in the Senate Amendment"
]

def passage_filter():
    return or_(*[VoteModel.question.ilike(f'%{kw}%') for kw in PASSAGE_KEYWORDS])

def procedural_exclusion():
    return not_(and_(
        BillModel.bill_type == 'HRES',
        BillModel.title.ilike('providing for consideration%')
    ))

# ROUTES
# Check API is working:
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


# Get individual member voting data for individual member pages
@app.route('/api/member/<string:member_id>')
def get_member(member_id):
    # Single query — fetch member info alongside filtered vote records
    m = MemberModel.query.filter_by(member_id=member_id).first_or_404()

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
        .filter(passage_filter())
        .filter(procedural_exclusion())
        .all()
    )

    return jsonify({
        'member_id':   m.member_id,
        'full_name':   m.full_name,
        'party':       m.party,
        'chamber':     m.chamber,
        'state_name':  m.state_name,
        'vote_records': [{
            'vote_id':    vr.vote_id,
            'vote_date':  vr.vote.vote_date.isoformat() if vr.vote.vote_date else None,
            'bill_title': vr.vote.bill.title,
            'bill_type':  vr.vote.bill.bill_type,
            'bill_num':   vr.vote.bill.bill_num,
            'question':   vr.vote.question,
            'position':   vr.position,
            'policy_area':vr.vote.bill.policy_area,
            'became_law': len(vr.vote.bill.laws) > 0,
        } for vr in vote_records]
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

    return jsonify([{
        'bill_id':      s.bill_id,
        'sponsor_type': s.sponsor_type,
        'bill_title':   s.bill.title        if s.bill else None,
        'bill_type':    s.bill.bill_type    if s.bill else None,
        'bill_num':     s.bill.bill_num     if s.bill else None,
        'policy_area':  s.bill.policy_area  if s.bill else None,
        'became_law':   len(s.bill.laws) > 0 if s.bill else False,
    } for s in sponsorships])


# DATA VISUALIZATIONS

# Bipartisanship within congress
@app.route('/api/visualizations/bipartisanship')
def get_bipartisanship():
    """
    Returns all passage votes with per-party yes/no/present/not-voting counts.
    All chamber / party / policy_area filtering is handled client-side.
    """
    votes = (
        VoteModel.query
        .join(VoteModel.bill)
        .options(
            contains_eager(VoteModel.bill),
            joinedload(VoteModel.vote_party_totals)
        )
        .filter(passage_filter())
        .filter(procedural_exclusion())
        .order_by(VoteModel.vote_date)
        .all()
    )

    return jsonify([{
        'vote_id':     v.vote_id,
        'vote_date':   v.vote_date.isoformat() if v.vote_date else None,
        'question':    v.question,
        'result':      v.result,
        'chamber':     v.chamber,
        'bill_id':     v.bill_id,
        'policy_area': v.bill.policy_area if v.bill else None,
        'party_totals': [{
            'party':            pt.party,
            'yes_count':        pt.yes_count,
            'no_count':         pt.no_count,
            'present_count':    pt.present_count,
            'not_voting_count': pt.not_voting_count,
            'yes_pct': round(
                pt.yes_count / (pt.yes_count + pt.no_count + pt.present_count)
                if (pt.yes_count + pt.no_count + pt.present_count) > 0 else 0,
                4
            )
        } for pt in v.vote_party_totals]
    } for v in votes])


@app.route('/api/visualizations/bill_funnel')
def get_bill_funnel_all():
    pass_result_filter = or_(
        *(VoteModel.result.ilike(f'%{r}%') for r in ["Passed"])
    )

    # Get all distinct policy areas (+ None bucket for "All")
    policy_areas = [r.policy_area for r in (
        db.session.query(BillModel.policy_area)
        .filter(BillModel.policy_area.isnot(None))
        .distinct().order_by(BillModel.policy_area).all()
    )]

    def get_stages(bill_ids_subq):
        introduced = db.session.query(func.count()).select_from(bill_ids_subq).scalar()
        voted_on = (
            db.session.query(func.count(distinct(VoteModel.bill_id)))
            .filter(VoteModel.bill_id.in_(bill_ids_subq))
            .scalar()
        )
        passed_one = (
            db.session.query(func.count(distinct(VoteModel.bill_id)))
            .filter(VoteModel.bill_id.in_(bill_ids_subq))
            .filter(pass_result_filter)
            .scalar()
        )
        became_law = (
            db.session.query(func.count(distinct(LawModel.bill_id)))
            .filter(LawModel.bill_id.in_(bill_ids_subq))
            .scalar()
        )
        return [
            {'label': 'Introduced',         'count': introduced},
            {'label': 'Voted On',           'count': voted_on},
            {'label': 'Passed One Chamber', 'count': passed_one},
            {'label': 'Became Law',         'count': became_law},
        ]

    result = {'All': get_stages(db.session.query(BillModel.bill_id).subquery())}

    for area in policy_areas:
        subq = (
            db.session.query(BillModel.bill_id)
            .filter(BillModel.policy_area == area)
            .subquery()
        )
        result[area] = get_stages(subq)

    return jsonify(result)


@app.route('/api/visualizations/activity_over_time')
def get_activity_over_time():
    """
    Returns vote counts grouped by week.
    All chamber / policy_area filtering is handled client-side.
    Raw vote dates are returned so the frontend can re-bucket by day/week/month.
    """
    votes = (
        VoteModel.query
        .join(VoteModel.bill)
        .options(contains_eager(VoteModel.bill))
        .filter(VoteModel.vote_date.isnot(None))
        .order_by(VoteModel.vote_date)
        .all()
    )

    return jsonify([{
        'vote_id':     v.vote_id,
        'vote_date':   v.vote_date.isoformat(),
        'chamber':     v.chamber,
        'policy_area': v.bill.policy_area if v.bill else None,
    } for v in votes])


@app.route('/api/visualizations/top_influencers')
def get_top_influencers():
    """
    Returns all primary sponsors with their law count, bills sponsored,
    and total cosponsors attracted — one row per member.
    All metric / chamber / party / policy_area filtering and ranking is client-side.
    """
    cosponsor_counts = (
        db.session.query(
            BillSponsorshipModel.bill_id,
            func.count(BillSponsorshipModel.member_id).label('n')
        )
        .filter(BillSponsorshipModel.sponsor_type == 'C')
        .group_by(BillSponsorshipModel.bill_id)
        .subquery()
    )

    rows = (
        db.session.query(
            MemberModel.member_id,
            MemberModel.full_name,
            MemberModel.party,
            MemberModel.chamber,
            MemberModel.state_name,
            BillModel.policy_area,
            func.count(distinct(BillSponsorshipModel.bill_id)).label('bills_sponsored'),
            func.count(distinct(LawModel.law_num)).label('laws_passed'),
            func.coalesce(func.sum(cosponsor_counts.c.n), 0).label('total_cosponsors')
        )
        .join(BillSponsorshipModel, MemberModel.member_id == BillSponsorshipModel.member_id)
        .join(BillModel, BillSponsorshipModel.bill_id == BillModel.bill_id)
        .outerjoin(LawModel, BillModel.bill_id == LawModel.bill_id)
        .outerjoin(cosponsor_counts, BillModel.bill_id == cosponsor_counts.c.bill_id)
        .filter(BillSponsorshipModel.sponsor_type == 'S')
        .group_by(
            MemberModel.member_id,
            MemberModel.full_name,
            MemberModel.party,
            MemberModel.chamber,
            MemberModel.state_name,
            BillModel.policy_area
        )
        .all()
    )

    return jsonify([{
        'member_id':       r.member_id,
        'full_name':       r.full_name,
        'party':           r.party,
        'chamber':         r.chamber,
        'state_name':      r.state_name,
        'policy_area':     r.policy_area,
        'bills_sponsored': r.bills_sponsored,
        'laws_passed':     r.laws_passed,
        'total_cosponsors':r.total_cosponsors,
    } for r in rows])


# HELPER: distinct policy areas
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
