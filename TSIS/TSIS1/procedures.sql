-- 1. add_phone(contact_name, phone, type)
--    Adds a phone number to an existing contact.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Validate type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- 2. move_to_group(contact_name, group_name)
--    Moves a contact to a group; creates the group if needed.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Find contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Find or create group
    SELECT id INTO v_group_id
    FROM groups
    WHERE name ILIKE p_group_name
    LIMIT 1;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name)
        RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;

    -- Move contact
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- 3. search_contacts(query)  →  TABLE
--    Full search: name, email, and all phone numbers.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id  INTEGER,
    name        VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    phones      TEXT,
    created_at  TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name         AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ')
                       AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.name  ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;


-- 4. Pagination helper
--    get_contacts_page(page_num, page_size, sort_by, group_id_filter)
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_page        INTEGER DEFAULT 1,
    p_size        INTEGER DEFAULT 10,
    p_sort        VARCHAR DEFAULT 'name',   -- 'name' | 'birthday' | 'created_at'
    p_group_id    INTEGER DEFAULT NULL,
    p_email_query VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    contact_id INTEGER,
    name       VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP,
    total_rows BIGINT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_offset INTEGER := (p_page - 1) * p_size;
    v_sort   TEXT;
BEGIN
    -- Whitelist sort column
    v_sort := CASE p_sort
        WHEN 'birthday'   THEN 'c.birthday'
        WHEN 'created_at' THEN 'c.created_at'
        ELSE 'c.name'
    END;

    RETURN QUERY EXECUTE format(
        'SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name,
            STRING_AGG(p.phone || '' ('' || COALESCE(p.type,''?'') || '')'', '', ''),
            c.created_at,
            COUNT(*) OVER ()
         FROM contacts c
         LEFT JOIN groups g ON g.id = c.group_id
         LEFT JOIN phones p ON p.contact_id = c.id
         WHERE ($1 IS NULL OR c.group_id = $1)
           AND ($2 IS NULL OR c.email ILIKE ''%%'' || $2 || ''%%'')
         GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
         ORDER BY %s NULLS LAST
         LIMIT $3 OFFSET $4',
        v_sort
    ) USING p_group_id, p_email_query, p_size, v_offset;
END;
$$;