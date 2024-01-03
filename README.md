# tmdb

A Go package for interacting with the v3 REST API of [The Movie Database](https://developer.themoviedb.org/docs).

This API client is autogenerated from the OpenAPI specification, which can be found [here](https://developer.themoviedb.org/openapi).

## Technical notes

The OpenAPI specification is retrieved and corrected with the [_tools/schema_gen.py](./_tools/schema_gen.py) script.

These corrections include:
 - unescaping JSON strings in examples
 - inferring missing schemas from examples
 - adding `nullable: true` where appropriate
 - removing technically duplicate properties (`_id` and `id`) and adding `additionalProperties: true` instead
 - changing `integer` types to `number` where appropriate (when examples contain a float)
 - removing additional characters in examples, which break the JSON syntax
 - replacing the security scheme for a `Bearer` token one

Some of these corrections come at the expense of decreasing the API ergonomics by loosening the schema constraints,
but it is done this way to save time when updating to a newer version of the schema.

## Updating

The API client can be re-generated with the `go generate` command.

A Python 3 installation is needed.

## Licensing

This library is licensed under the [MIT License](./LICENSE), but the OpenAPI specification is the property of [The Movie Database](https://developer.themoviedb.org/docs).
