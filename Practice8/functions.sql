CREATE OR REPLACE FUNCTION find_contacts(pattern TEXT)
RETURNS TABLE (id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT user_id, user_name, phone_number
    FROM contacts
    WHERE user_name ILIKE '%' || pattern || '%'
        OR phone_number LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paged(p_limit INT, p_offset INT)
RETURNS TABLE (id INT, user_name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.user_id, c.user_name, c.phone_number
    FROM contacts AS c
    ORDER BY user_id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;