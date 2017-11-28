# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-28 00:51
from __future__ import unicode_literals

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


add_search_trigger = """
CREATE EXTENSION unaccent;

CREATE TEXT SEARCH CONFIGURATION simple_unaccented ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION simple_unaccented
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, simple;

CREATE FUNCTION email_to_tsvector(email people_personemail.address%TYPE) RETURNS tsvector AS $$
DECLARE
  email_parts text[];
BEGIN
  email_parts := string_to_array(email, '@');
  RETURN 
    setweight(
      to_tsvector('simple_unaccented', email) ||
      to_tsvector('simple_unaccented', regexp_replace(email_parts[1], '[-._]', ' ', 'g')) ,
    'A') ||
    setweight(to_tsvector('simple_unaccented', email_parts[2]), 'D');
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION get_people_tsvector(
  _id people_person.id%TYPE, first_name people_person.first_name%TYPE,
  last_name people_person.last_name%TYPE, location_zip people_person.location_zip%TYPE
) RETURNS tsvector AS $$
DECLARE
  email RECORD;
  search tsvector;
BEGIN
    --
    -- Return the search vector associated with the person information
    --
    search :=
      setweight(
        to_tsvector('simple_unaccented', coalesce(first_name, '')) || 
        to_tsvector('simple_unaccented', coalesce(last_name, '')), 'B'
      ) ||
      setweight(to_tsvector('simple_unaccented', coalesce(location_zip, '')), 'D');
    
    FOR email in SELECT address FROM people_personemail WHERE person_id = _id LOOP
      search := search || email_to_tsvector(email.address);
END LOOP;

RETURN search;
END;
$$ LANGUAGE plpgsql;
  
CREATE FUNCTION process_update_person() RETURNS TRIGGER AS $$
DECLARE
    do_update bool default FALSE;
    email RECORD;
    temp_search tsvector;
BEGIN
    --
    -- Trigger function to update search field on person when she is updated
    -- No need to do it in creation: initialization of the search field
    -- will be done when first email will be created.
    --
    IF (NEW.first_name <> OLD.first_name) THEN do_update = TRUE;
    ELSIF (NEW.last_name <> OLD.last_name) THEN do_update = TRUE;
    ELSIF (NEW.location_zip <> OLD.location_zip) THEN do_update = TRUE;
    END IF;
    
    IF do_update THEN
        NEW.search := get_people_tsvector(NEW.id, NEW.first_name, NEW.last_name, NEW.location_zip);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_people_search_field_from_id(person_id people_person.id%TYPE) RETURNS VOID AS $$
BEGIN
  --
  -- Update search vector for the person identified by person_id
  -- 
  UPDATE people_person SET search = get_people_tsvector(id, first_name, last_name, location_zip) WHERE id = person_id;
END
$$ LANGUAGE plpgsql;
  
CREATE FUNCTION process_update_email() RETURNS TRIGGER AS $$
BEGIN
  --
  -- Trigger function to update the corresponding person's search vector
  -- when an email is inserted, updated or delete
  --
  IF (tg_op = 'INSERT') THEN
    PERFORM update_people_search_field_from_id(NEW.person_id);
  ELSIF (tg_op = 'DELETE') THEN
    PERFORM update_people_search_field_from_id(OLD.person_id);
  ELSIF (tg_op = 'UPDATE' AND (OLD.address <> NEW.address OR OLD.person_id <> NEW.person_id)) THEN
    PERFORM update_people_search_field_from_id(NEW.person_id);
  END IF;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_person_search_field_when_modified
BEFORE UPDATE ON people_person
  FOR EACH ROW EXECUTE PROCEDURE process_update_person();
  
CREATE TRIGGER update_search_field_when_email_modified
AFTER INSERT OR UPDATE OR DELETE ON people_personemail
  FOR EACH ROW EXECUTE PROCEDURE process_update_email();
  
UPDATE people_person SET search = get_people_tsvector(id, first_name, last_name, location_zip);
"""


remove_search_trigger = """
DROP TRIGGER update_search_field_when_email_modified ON people_personemail;
DROP FUNCTION process_update_email();
DROP FUNCTION update_people_search_field_from_id(people_person.id%TYPE);
DROP TRIGGER update_person_search_field_when_modified ON people_person;
DROP FUNCTION process_update_person();
DROP FUNCTION get_people_tsvector(
  people_person.id%TYPE, people_person.first_name%TYPE, people_person.last_name%TYPE, people_person.location_zip%TYPE
);
DROP FUNCTION email_to_tsvector(people_personemail.address%TYPE);
DROP TEXT SEARCH CONFIGURATION simple_unaccented;
DROP EXTENSION unaccent;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0020_auto_20171113_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='search',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True, verbose_name='Données de recherche'),
        ),
        migrations.RunSQL(
            sql=add_search_trigger,
            reverse_sql=remove_search_trigger
        ),
        migrations.AddIndex(
            model_name='person',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search'], name='search_index'),
        ),
    ]
