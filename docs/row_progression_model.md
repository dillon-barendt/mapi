---

## How It Works

1. **Row Model**
   • Pydantic’s “BaseModel” enforces type hints (string for “name”, int for “position”).
   • The validators check each field. For example, “check_name” ensures only certain characters are allowed.

2. **RowProgression Model**
   • Holds the entire code string (e.g., “A, B, 123”).
   • Uses a “root_validator(pre=True)” that runs before standard validation. This is where parsing of the “code” field occurs.
   • Each segment from “code” is converted into a “Row” object. Any parse or validation errors in “Row” will bubble up here.
   • The “rows” field is then set to that list of “Row” objects.

3. **Usage**
   • Simply instantiate “rp = RowProgression(code=’A, B, 123’)”. If the parse or any row-level validation fails, Pydantic raises a descriptive exception.
   • You can access the resulting “rows” as a list of “Row” objects.
   • The convenience property “row_count” shows the total number of parsed rows.

4. **Extension**
   • Modify the parse logic in “root_validator” to handle more advanced features, e.g., range expansions (like “A:Z”), position gaps, or equivalences (like “A=B”).
   • Enhance the “Row” model with more fields or constraints as needed.

With this design, you get end-to-end validation—both individual rows and the entire code string—while still having flexible parsing in one place.
