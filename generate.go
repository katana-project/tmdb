package tmdb

//go:generate python3 _tools/schema_gen.py
//go:generate ogen --generate-tests --no-server --package tmdb --target . openapi.json
