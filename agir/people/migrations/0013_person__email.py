# Generated by Django 3.1.13 on 2021-12-13 12:45

from django.db import migrations, models


DROP_PERSON_EMAIL_TRIGGERS_AND_FUNCTIONS = """
DROP TRIGGER IF EXISTS update_person__email_field_when_email_modified ON people_personemail;
DROP FUNCTION IF EXISTS get_person_primary_email(people_person.id%TYPE);
DROP FUNCTION IF EXISTS update_people_person__email_field_from_id(people_person.id%TYPE);
DROP FUNCTION IF EXISTS process_update_person_email();
"""

CREATE_PERSON_EMAIL_TRIGGERS_AND_FUNCTIONS = """
CREATE FUNCTION get_person_primary_email(person_pk people_person.id%TYPE) RETURNS text AS $$
BEGIN
  --
  -- Retrieve the primary email address for the person
  --
  RETURN COALESCE((
    SELECT address FROM people_personemail 
    WHERE person_id = person_pk   
    ORDER BY "bounced", "_order" 
    LIMIT 1
  ), '');
END
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_people_person__email_field_from_id(person_id people_person.id%TYPE) RETURNS VOID AS $$
BEGIN
  --
  -- Update _email field for the person identified by person_id
  --
  UPDATE people_person pp SET _email = get_person_primary_email(person_id) WHERE id =  person_id;
END
$$ LANGUAGE plpgsql;

CREATE FUNCTION process_update_person_email() RETURNS TRIGGER AS $$
BEGIN
  --
  -- Trigger function to update the corresponding person's primary email
  -- when an email is created, updated or deleted
  --
  IF (tg_op = 'INSERT') THEN
    PERFORM update_people_person__email_field_from_id(NEW.person_id);
  ELSIF (tg_op = 'DELETE') THEN
    PERFORM update_people_person__email_field_from_id(OLD.person_id);
  ELSIF (tg_op = 'UPDATE') THEN
    PERFORM update_people_person__email_field_from_id(NEW.person_id);
  END IF;
    RETURN NULL;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_person__email_field_when_email_modified
AFTER INSERT OR UPDATE OR DELETE ON people_personemail
  FOR EACH ROW EXECUTE PROCEDURE process_update_person_email();

UPDATE people_person SET _email = get_person_primary_email(id);
"""


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0012_personform_short_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="_email",
            field=models.EmailField(
                default="",
                editable=False,
                help_text="L'adresse email principale de la personne",
                max_length=254,
                verbose_name="adresse email",
            ),
        ),
        migrations.RunSQL(
            sql=CREATE_PERSON_EMAIL_TRIGGERS_AND_FUNCTIONS,
            reverse_sql=DROP_PERSON_EMAIL_TRIGGERS_AND_FUNCTIONS,
        ),
    ]
