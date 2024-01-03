package tmdb

//go:generate python3 _tools/schema_gen.py
//go:generate go run github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@latest --config models.cfg.yaml openapi.json
//go:generate go run github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@latest --config client.cfg.yaml openapi.json
