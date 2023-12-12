package tmdb

//go:generate python3 _tools/schema_gen.py
//go:generate go run github.com/ogen-go/ogen/cmd/ogen@v0.80.1 --config generate.yml --package tmdb --target . openapi.json
