from main import GDSFParser

parser = GDSFParser("example.gdsf")
mechanics = parser.get_schemas_by_type("mechanic")
components = parser.get_schemas_by_type("component")

print(mechanics)
print(components)