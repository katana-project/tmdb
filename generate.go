package tmdb

//go:generate python3 _tools/schema_gen.py
//go:generate go run github.com/ogen-go/ogen/cmd/ogen@v0.75.0 --generate-tests --no-server --package tmdb --target . openapi.json
