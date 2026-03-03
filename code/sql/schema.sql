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
    state_name TEXT,
    district INT, 
    years_in_congress INT,
    age INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bills (
    bill_id TEXT PRIMARY KEY,
    bill_type TEXT,
    bill_num INT,
    congress INT,
    chamber CHAR(1),
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE amendments (
    amendment_id TEXT PRIMARY KEY,
    amendment_type TEXT,
    congress INT,
    chamber CHAR(1),
    purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE votes (
    vote_id VARCHAR(17) PRIMARY KEY,
    bill_id TEXT,
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
    vote_id VARCHAR(17),
    member_id VARCHAR(8),
    position TEXT,

    PRIMARY KEY (vote_id, member_id),

    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)

);

CREATE TABLE vote_party_totals (
    vote_id VARCHAR(17),
    party CHAR(1),
    yes_count INT,
    no_count INT,
    present_count INT,
    not_voting_count INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (vote_id, party),

    FOREIGN KEY (vote_id) REFERENCES votes(vote_id),
);