/*
SQL script for creating tables in postgres database
*/

CREATE TABLE members (
    member_id VARCHAR(8) PRIMARY KEY,
    full_name TEXT,
    first_name TEXT,
    last_name TEXT,
    party CHAR(1),
    chamber CHAR(1),
    state_name CHAR(2),
    district INT, 
    years_in_congress INT,
    age INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bills (
    bill_id VARCHAR(20) PRIMARY KEY,
    bill_type TEXT,
    bill_num INT,
    congress INT,
    chamber CHAR(1),
    title TEXT,
    policy_area TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE votes (
    vote_id VARCHAR(20) PRIMARY KEY,
    bill_id VARCHAR(20),
    question TEXT,
    chamber CHAR(1),
    congress INT,
    session_num INT,
    vote_date TIMESTAMPTZ,
    result TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);


CREATE TABLE vote_records (
    vote_id VARCHAR(20),
    member_id VARCHAR(8),
    position TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (vote_id, member_id),

    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)

);

CREATE TABLE vote_party_totals (
    vote_id VARCHAR(20),
    party CHAR(1),
    yes_count INT,
    no_count INT,
    present_count INT,
    not_voting_count INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (vote_id, party),

    FOREIGN KEY (vote_id) REFERENCES votes(vote_id)
);

CREATE TABLE bill_sponsorships (
    bill_id VARCHAR(20),
    member_id VARCHAR(8),
    sponsor_type CHAR(1),  -- 'S' = sponsor, 'C' = cosponsor
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (bill_id, member_id, sponsor_type),

    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE laws (
    law_num TEXT PRIMARY KEY,
    law_type TEXT,
    bill_id VARCHAR(20),
    law_date TIMESTAMPTZ,
    congress INT,
    chamber CHAR(1),

    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);