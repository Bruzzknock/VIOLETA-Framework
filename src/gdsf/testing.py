from main import GDSFParser

parser = GDSFParser("example.gdsf")
mechanics = parser.get_schemas_by_type("mechanic")
components = parser.get_schemas_by_type("component")
atomic_skills = parser.get_section("atomic_skills")

print(mechanics)
print(components)
print(atomic_skills)