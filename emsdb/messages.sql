BEGIN;


-- templates

CREATE TYPE messages.template_language AS ENUM ('jinja2')
;

CREATE TYPE messages.template_status 
AS ENUM ('active', 'not_active');
;

CREATE TABLE messages.TEMPLATE (
    NAME text PRIMARY KEY,
    STATUS messages.template_status DEFAULT 'not_active',
    BODY text NOT NULL,
    LANGUAGE messages.template_language NOT NULL
)
;

CREATE OR REPLACE VIEW messages.V_TEMPLATE_ACTIVE AS
SELECT 
    NAME, BODY, LANGUAGE
FROM 
    messages.TEMPLATE
WHERE
    STATUS = 'active'
;


-- messages

CREATE TYPE messages.message_status 
AS ENUM ('active', 'not_active');
;

CREATE TYPE messages.message_part 
AS ENUM ('body', 'subject', 'headers', 'attachment-name', 'sender');
;

CREATE TYPE messages.message_channel 
AS ENUM ('email', 'mobile-push', 'browser-push', 'sms', 'phone-call', 'paper-mail', 'http-request');
;

CREATE TABLE messages.MESSAGE (
    NAME text PRIMARY KEY,
    STATUS messages.message_status DEFAULT 'not_active',
    CHANNEL messages.message_channel NOT NULL,
    REQUIRED_PARTS messages.message_part[] NOT NULL
)
;

CREATE TABLE messages.MESSAGE_PARTS (
    MESSAGE_NAME text NOT NULL CONSTRAINT FK_MP_MESSAGE_NAME REFERENCES messages.MESSAGE(NAME) ON DELETE CASCADE,
    PART messages.message_part NOT NULL,
    TEMPLATE_NAME text NOT NULL CONSTRAINT FK_MP_TEMPLATE_NAME REFERENCES messages.TEMPLATE(NAME) ON DELETE CASCADE,

    CONSTRAINT UQ_MP_MESSAGE_NAME_PART UNIQUE (MESSAGE_NAME, PART)
)
;

CREATE OR REPLACE VIEW messages.V_MESSAGE_ACTIVE AS
SELECT 
    NAME, REQUIRED_PARTS, CHANNEL
FROM
    messages.MESSAGE
WHERE 
    STATUS = 'active'
;

CREATE OR REPLACE VIEW messages.V_MESSAGE_ACTIVE_PARTS AS 
SELECT 
    m.NAME, mp.PART, t.NAME as TEMPLATE_NAME, t.BODY as TEMPLATE_BODY, t.LANGUAGE as TEMPLATE_LANGUAGE
FROM
    messages.V_MESSAGE_ACTIVE m 
    JOIN (
        SELECT MESSAGE_NAME, PART, TEMPLATE_NAME, array_agg(PART) OVER (PARTITION BY MESSAGE_NAME) PRESENTED_PARTS
        FROM messages.MESSAGE_PARTS
    ) mp ON (m.NAME = mp.MESSAGE_NAME)
    JOIN messages.V_TEMPLATE_ACTIVE t ON (t.NAME = mp.TEMPLATE_NAME)
WHERE
    mp.PRESENTED_PARTS @> m.REQUIRED_PARTS
;


-- triggers

CREATE TYPE messages.trigger_filter_status
AS ENUM ('active', 'not_active');
;

CREATE TABLE messages.TRIGGER_FILTER (
    NAME text PRIMARY KEY,
    STATUS messages.trigger_filter_status DEFAULT 'not_active'
)
;

CREATE OR REPLACE VIEW messages.V_TRIGGER_FILTER_ACTIVE AS
SELECT 
    NAME
FROM
    messages.TRIGGER_FILTER
WHERE 
    STATUS = 'active'
;

CREATE TYPE messages.trigger_processor_status
AS ENUM ('active', 'not_active');
;

CREATE TABLE messages.TRIGGER_PROCESSOR (
    NAME text PRIMARY KEY,
    STATUS messages.trigger_processor_status DEFAULT 'not_active'
)
;

CREATE OR REPLACE VIEW messages.V_TRIGGER_PROCESSOR_ACTIVE AS
SELECT 
    NAME
FROM
    messages.TRIGGER_PROCESSOR
WHERE 
    STATUS = 'active'
;

CREATE TYPE messages.trigger_type_status 
AS ENUM ('active', 'not_active');
;

CREATE TABLE messages.TRIGGER_TYPE (
    NAME text PRIMARY KEY,
    STATUS messages.trigger_type_status DEFAULT 'not_active'
)
;

CREATE TABLE messages.TRIGGER_TYPE_FILTERS (
    TRIGGER_TYPE_NAME text NOT NULL CONSTRAINT FK_TTF_TRIGGER_TYPE_NAME REFERENCES messages.TRIGGER_TYPE(NAME) ON DELETE CASCADE,
    TRIGGER_FILTER_NAME text NOT NULL CONSTRAINT FK_TTF_TRIGGER_FILTER_NAME REFERENCES messages.TRIGGER_FILTER(NAME) ON DELETE CASCADE
)
;

CREATE TABLE messages.TRIGGER_TYPE_PROCESSORS (
    TRIGGER_TYPE_NAME text NOT NULL CONSTRAINT FK_TTP_TRIGGER_TYPE_NAME REFERENCES messages.TRIGGER_TYPE(NAME) ON DELETE CASCADE,
    TRIGGER_PROCESSOR_NAME text NOT NULL CONSTRAINT FK_TTP_TRIGGER_PROCESSOR_NAME REFERENCES messages.TRIGGER_PROCESSOR(NAME) ON DELETE CASCADE
)
;

CREATE OR REPLACE VIEW messages.V_TRIGGER_TYPE_ACTIVE AS
SELECT 
    tt.NAME, ttf.FILTER_NAMES, ttp.PROCESSOR_NAMES
FROM
    messages.TRIGGER_TYPE tt
    LEFT JOIN (
        SELECT TRIGGER_TYPE_NAME, array_agg(TRIGGER_FILTER_NAME) FILTER_NAMES
        FROM 
            messages.TRIGGER_TYPE_FILTERS ttf
            JOIN messages.V_TRIGGER_FILTER_ACTIVE tf ON (ttf.TRIGGER_FILTER_NAME = tf.NAME)
        GROUP BY TRIGGER_TYPE_NAME
    ) ttf ON (tt.NAME = ttf.TRIGGER_TYPE_NAME)
    LEFT JOIN (
        SELECT TRIGGER_TYPE_NAME, array_agg(TRIGGER_PROCESSOR_NAME) PROCESSOR_NAMES
        FROM 
            messages.TRIGGER_TYPE_PROCESSORS ttp
            JOIN messages.V_TRIGGER_PROCESSOR_ACTIVE tp ON (ttp.TRIGGER_PROCESSOR_NAME = tp.NAME)
        GROUP BY TRIGGER_TYPE_NAME
    ) ttp ON (tt.NAME = ttp.TRIGGER_TYPE_NAME)
WHERE 
    tt.STATUS = 'active'
;

CREATE TYPE messages.trigger_type_message_status 
AS ENUM ('active', 'not_active');
;

CREATE TABLE messages.TRIGGER_TYPE_MESSAGES (
    TRIGGER_TYPE_NAME text NOT NULL CONSTRAINT FK_TTM_TRIGGER_TYPE_NAME REFERENCES messages.TRIGGER_TYPE(NAME) ON DELETE CASCADE,
    MESSAGE_NAME text NOT NULL CONSTRAINT FK_TTM_MESSAGE_NAME REFERENCES messages.MESSAGE(NAME) ON DELETE CASCADE,
    STATUS messages.trigger_processor_status DEFAULT 'not_active',

    CONSTRAINT UQ_TTM_TRIGGER_TYPE_MESSAGE_NAME UNIQUE (TRIGGER_TYPE_NAME, MESSAGE_NAME)
)
;

CREATE TYPE messages.template_tuple AS (
    name text,
    body text,
    language messages.template_language
);

CREATE OR REPLACE VIEW messages.V_TRIGGER_TYPE_MESSAGES_ACTIVE AS
SELECT 
    ttm.TRIGGER_TYPE_NAME, ttm.MESSAGE_NAME, tt.FILTER_NAMES, tt.PROCESSOR_NAMES, m.TEMPLATES
FROM 
    messages.TRIGGER_TYPE_MESSAGES ttm
    JOIN messages.V_TRIGGER_TYPE_ACTIVE tt ON (ttm.TRIGGER_TYPE_NAME = tt.NAME)
    JOIN (
        SELECT NAME, array_agg((TEMPLATE_NAME, TEMPLATE_BODY, TEMPLATE_LANGUAGE)::messages.template_tuple) TEMPLATES
        FROM messages.V_MESSAGE_ACTIVE_PARTS
        GROUP BY NAME
    ) m ON (ttm.MESSAGE_NAME = m.NAME)
WHERE 
    ttm.STATUS = 'active'
;

COMMIT;