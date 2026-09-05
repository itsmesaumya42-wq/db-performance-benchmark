-- schema.sql
-- Core table used to benchmark indexing strategies.
-- Deliberately created WITHOUT indexes first (except PK) so you can
-- measure the "before" state, then add indexes and measure "after".

DROP TABLE IF EXISTS transactions CASCADE;

CREATE TABLE transactions (
    transaction_id   BIGSERIAL PRIMARY KEY,
    card_number      VARCHAR(20)   NOT NULL,
    merchant_id      INT           NOT NULL,
    merchant_category VARCHAR(30)  NOT NULL,
    amount           DECIMAL(12,2) NOT NULL,
    currency         VARCHAR(3)    NOT NULL DEFAULT 'USD',
    country_code     VARCHAR(2)    NOT NULL,
    status           VARCHAR(20)   NOT NULL, -- APPROVED, DECLINED, REVERSED
    created_at       TIMESTAMP     NOT NULL
);

-- Reference table for merchants, used in JOIN benchmarks
DROP TABLE IF EXISTS merchants CASCADE;

CREATE TABLE merchants (
    merchant_id      SERIAL PRIMARY KEY,
    merchant_name    VARCHAR(100) NOT NULL,
    category         VARCHAR(30)  NOT NULL,
    country_code     VARCHAR(2)   NOT NULL
);
