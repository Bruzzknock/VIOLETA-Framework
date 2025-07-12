class GDSFParser:
    def __init__(self, filepath):
        self.edges = []
        self.meta = {}
        self.sections = {}
        self.schemas = []
        self.seen_ids = set()
        self._parse(filepath)

    def _parse(self, filepath):
        section = None
        current = {}
        line_num = 0
        with open(filepath) as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    if section == "schema" and current:
                        self._append_validated_schema(current,line_num)
                    elif section == "edge" and current:
                        self.edges.append(current)
                    elif section == "meta" and current:
                        self.meta.update(current)
                    elif section and current:
                        self.sections[section] = current
                    section = line[1:-1]
                    current = {}
                else:
                    key, value = line.split("=", 1)
                    current[key.strip()] = value.strip().strip('"')

            # Add last entry
            if section == "schema":
                self._append_validated_schema(current,line_num)
            elif section == "edge":
                self.edges.append(current)
            elif section == "meta":
                self.meta.update(current)
            elif section and current:
                self.sections[section] = current
    
    def _validate_schema(self, schema, line_num):
        prop = schema.get("property").replace(" ", "")
        schema_id = schema.get("id")

        if "name" not in schema:
            raise ValueError(f"Missing property 'name' in schema on line {line_num}.")

        name = schema.get("name").replace(" ", "")

        if len(name) == 0:
            raise ValueError(f"Missing 'name' in schema on line {line_num}.")
        
        if not schema_id:
            raise ValueError(f"Missing 'id' in schema on line {line_num}.")
        
        if schema_id in self.seen_ids:
            raise ValueError(
                f"Duplicate schema ID '{schema_id}' found on line {line_num}."
            )
        
        self.seen_ids.add(schema_id)

        if prop and (";" in prop or "," in prop):
            raise ValueError(
                f"Schema '{schema.get('id', '?')}' has multiple properties on line {line_num}: '{prop}'. "
                f"Only one property is allowed (e.g., 'component' or 'mechanic')."
            )
        
    def _append_validated_schema(self,schema,line_num):
        self._validate_schema(schema, line_num)
        self.schemas.append(schema)

    def get_schemas_by_type(self, property_type):
        return [s for s in self.schemas if s.get("property") == property_type]
    
    def get_section(self, name):
        return self.sections.get(name, {})
