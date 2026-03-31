CREATE OR REPLACE PROCEDURE insert_update_contact(p_name TEXT, p_phone TEXT) AS $$
BEGIN
    INSERT INTO contacts (user_name, phone_number)
    VALUES (p_name, p_phone)
    ON CONFLICT (user_name)
    DO UPDATE SET phone_number = EXCLUDED.phone_number;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE mass_insert_contacts(
    p_names TEXT[],
    p_phones TEXT[],
    OUT incorrect_data TEXT[]
) AS $$
DECLARE
    i INT;
BEGIN
    incorrect_data := '{}';
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        IF length(p_phones[i]) BETWEEN 10 AND 15 THEN
            INSERT INTO contacts (user_name, phone_number)
            VALUES (p_names[i], p_phones[i])
            ON CONFLICT (user_name)
            DO UPDATE SET phone_number = EXCLUDED.phone_number;
        ELSE
            incorrect_data := array_append(incorrect_data, p_names[i] || ':' || p_phones[i]);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_contact(p_identifier TEXT) AS $$
BEGIN
    DELETE FROM contacts
    WHERE user_name = p_identifier
        OR phone_number = p_identifier;
    IF NOT FOUND THEN
        RAISE NOTICE 'Contact % was not found.', p_identifier;
    END IF;
END;
$$ LANGUAGE plpgsql;