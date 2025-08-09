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
        pending_key = None
        pending_lines: list[str] = []
        with open(filepath) as f:
            for line_num, raw_line in enumerate(f, start=1):
                stripped = raw_line.strip()

                if pending_key is not None:
                    # We are collecting a multi-line value. Preserve exact
                    # line contents (without the trailing newline) including
                    # blank lines.
                    pending_lines.append(raw_line.rstrip("\n"))
                    if stripped.endswith('"'):
                        value = "\n".join(pending_lines).strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        current[pending_key] = value
                        pending_key = None
                        pending_lines = []
                    continue

                if not stripped or stripped.startswith("#"):
                    continue

                if stripped.startswith("[") and stripped.endswith("]"):
                    if section == "schema" and current:
                        self._append_validated_schema(current, line_num)
                    elif section == "edge" and current:
                        self.edges.append(current)
                    elif section == "meta" and current:
                        self.meta.update(current)
                    elif section and current:
                        self.sections[section] = current
                    section = stripped[1:-1]
                    current = {}
                else:
                    if "=" not in raw_line:
                        # Ignore malformed lines outside of a multi-line value
                        continue
                    key, value = raw_line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and not value.endswith('"'):
                        # Begin multi-line value and continue collecting in
                        # subsequent iterations until we hit a closing quote.
                        pending_key = key
                        pending_lines = [value]
                    else:
                        current[key] = value.strip('"')

            # Add last entry
            if pending_key is not None:
                value = "\n".join(pending_lines).strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                current[pending_key] = value
            if section == "schema":
                self._append_validated_schema(current, line_num)
            elif section == "edge":
                self.edges.append(current)
            elif section == "meta":
                self.meta.update(current)
            elif section and current:
                self.sections[section] = current
    
    def _validate_schema(self, schema, line_num):
        prop = schema.get("property", "").replace(" ", "")
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
