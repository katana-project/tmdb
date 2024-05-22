package tmdb

//go:generate python3 _tools/schema_gen.py
//go:generate go run github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@v2.1.0 --config models.cfg.yaml openapi.json
//go:generate go run github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@v2.1.0 --config client.cfg.yaml openapi.json
