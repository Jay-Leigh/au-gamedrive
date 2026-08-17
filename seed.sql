CREATE TABLE approved_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account VARCHAR NOT NULL,
    audience_name VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    destination JSON NOT NULL,
    is_active BOOLEAN NOT NULL,
    UNIQUE (account, audience_name, platform)
);
CREATE INDEX ix_approved_accounts_account ON approved_accounts (account);

CREATE TABLE batch_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account VARCHAR NOT NULL,
    batch_id VARCHAR NOT NULL,
    request_id VARCHAR NOT NULL,
    UNIQUE (account, batch_id)
);
CREATE INDEX ix_batch_registrations_account ON batch_registrations (account);

CREATE TABLE checkpoint_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id VARCHAR(36) NOT NULL,
    checkpoint VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    raw_payload JSON,
    source_system VARCHAR(30) NOT NULL DEFAULT 'audience_uploader',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_checkpoint_logs_request_id ON checkpoint_logs (request_id);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id VARCHAR(36) NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    account VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    audience_name VARCHAR(100) NOT NULL,
    source_system VARCHAR(30) NOT NULL DEFAULT 'audience_uploader',
    total_rows INTEGER NOT NULL,
    valid_rows INTEGER NOT NULL,
    invalid_rows JSON,
    dispatched INTEGER NOT NULL,
    succeeded INTEGER NOT NULL,
    failed JSON,
    overall_status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_audit_logs_request_id ON audit_logs (request_id);

INSERT INTO approved_accounts (account, audience_name, platform, destination, is_active) VALUES
('realbeds', 'QualifiedLead', 'meta', '{"audience_id": "120253772920450348"}', true),
('realbeds', 'BedZoneQualifiedLead', 'meta', '{"audience_id": "120254471375470348"}', true),
('realbeds', 'testCombinedfile', 'meta', '{"audience_id": "120254650290030348"}', true),
('realbeds', 'QualifiedLead', 'googleads', '{"customer_id": "7092652546", "user_list_id": "9425866437"}', true)
ON CONFLICT (account, audience_name, platform) DO NOTHING;