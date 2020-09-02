from django.db import migrations

FIX_TRIGGER = """
DROP TRIGGER update_person_search_field_when_modified ON people_person;

CREATE TRIGGER update_person_search_field_when_modified
BEFORE INSERT OR UPDATE ON people_person
  FOR EACH ROW EXECUTE PROCEDURE process_update_person();
"""

UNFIX_TRIGGER = """
DROP TRIGGER update_person_search_field_when_modified ON people_person

CREATE TRIGGER update_person_search_field_when_modified
BEFORE UPDATE ON people_person
  FOR EACH ROW EXECUTE PROCEDURE process_update_person();
"""


class Migration(migrations.Migration):
    dependencies = [("people", "0066_auto_20200723_1616")]

    operations = [migrations.RunSQL(sql=FIX_TRIGGER, reverse_sql=UNFIX_TRIGGER)]
