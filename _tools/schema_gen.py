from argparse import ArgumentParser
from urllib.request import Request, urlopen
from re import compile
from json import loads, dump

HEADERS = {"User-Agent": "Mozilla/5.0"}

LINK_PATTERN = compile(r'<a href="([a-z0-9/]+)">TMDB API - v3</a>')


def merge_schema(a: dict[str, any], b: dict[str, any]):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_schema(a[key], b[key])
            else:
                if key == "type":  # perform type checks
                    if a[key] == "number" and b[key] == "integer":
                        continue  # don't downcast fp numbers to integers

                a[key] = b[key]  # key exists, replace value
        else:  # key missing entirely, add value
            a[key] = b[key]


def infer_schema_type(node: any) -> dict[str, any]:
    if isinstance(node, bool):
        return {"type": "boolean", "example": node}
    elif isinstance(node, int):
        return {"type": "integer", "example": node}
    elif isinstance(node, str):
        return {"type": "string", "example": node}
    elif isinstance(node, float):
        return {"type": "number", "example": node}
    elif isinstance(node, list):
        schem = {"type": "array", "items": {}}
        for item in node:  # infer schema from all items
            merge_schema(schem["items"], infer_schema_type(item))

        return schem
    elif isinstance(node, dict):
        return {"type": "object", "properties": {k: infer_schema_type(v) for k, v in node.items()}}
    elif node is None:  # for inferring nullability when merging schemas
        return {"nullable": True}

    raise Exception(f"Could not infer schema type of {node}")


def clean_schema_tree(node: list | dict[str, any], path: list[str] = None):
    if path is None:
        path = []

    if isinstance(node, dict):
        for k, v in list(node.items()):
            item_path = [*path, k]

            if isinstance(v, dict):
                # check duplicate properties after removing escape symbols
                if k == "properties":
                    keys = set()

                    for k1, v1 in sorted(v.items(), reverse=True, key=(lambda e: e[0])):
                        clean_key = k1.strip("_")
                        if clean_key in keys:
                            del v[k1]
                            node["additionalProperties"] = True

                            print(f"removed duplicate property {k1} -> {clean_key}, path: {'.'.join([*item_path, k1])}")

                        keys.add(clean_key)
                elif k == "application/json" and "examples" in v:
                    (example_obj_key, example_obj) = next(iter(v["examples"].items()))

                    example_value = example_obj["value"]
                    if isinstance(example_value, str) and \
                            ((example_value.startswith("{") and example_value.endswith("}"))
                             or (example_value.startswith("[") and example_value.endswith("]"))):
                        example_value = loads(example_value)
                        example_obj["value"] = example_value

                        print(f"fixed escaped example, path: {'.'.join([*item_path, 'examples', example_obj_key])}")

                    inferred_schema = infer_schema_type(example_value)
                    if "schema" not in v:  # check missing schema
                        v["schema"] = inferred_schema

                        print(f"fixed missing schema, path: {'.'.join(item_path)}")
                    else:  # enrich existing schema
                        merge_schema(v["schema"], inferred_schema)
                elif k == "sec0" and item_path[-2] == "securitySchemes":  # check wrong security scheme
                    # it is just an Authorization header scheme by default, we want it to be a Bearer token
                    node[k] = {
                        "type": "http",
                        "scheme": "bearer"
                    }
                    print(f"fixed wrong security scheme, path: {'.'.join(item_path)}")
                elif k == "RAW_BODY":  # check raw body properties
                    del node[k]

                    print(f"removed raw body property, path: {'.'.join(item_path)}")
                elif (k.endswith("_path") or k.startswith("iso_")) and "type" not in v:
                    # MANUAL FIX: paths and ISO codes are always strings
                    v["type"] = "string"

                    print(f"fixed missing type, path: {'.'.join(item_path)}")

                clean_schema_tree(v, path=item_path)
            elif isinstance(v, list):
                if k == "required" and "RAW_BODY" in v:  # check raw body property requirement
                    v.remove("RAW_BODY")

                    print(f"removed raw body property requirement, path: {'.'.join(item_path)}")

                clean_schema_tree(v, path=item_path)
            elif k == "default" and v is None:  # check null default
                node["nullable"] = True

                print(f"fixed null default, path: {'.'.join(item_path)}")
    else:
        for i, v in enumerate(node):
            if isinstance(v, dict) or isinstance(v, list):
                clean_schema_tree(v, path=[*path, str(i)])


if __name__ == "__main__":
    parser = ArgumentParser(description="Downloads and fixes the TMDB v3 API OpenAPI specification.")
    parser.add_argument("--url", "-u", help="the base URL of the TMDB developer documentation",
                        default="https://developer.themoviedb.org")
    parser.add_argument("--output", "-o", help="the schema file output", default="./openapi.json")

    p_args = parser.parse_args()

    with urlopen(Request(url=f"{p_args.url}/openapi", headers=HEADERS)) as r:
        html_body = r.read().decode("utf-8")

    m = LINK_PATTERN.search(html_body)
    if not m:
        raise Exception(f"Did not find TMDB v3 API link in {html_body}")

    with urlopen(Request(url=f"{p_args.url}{m.group(1)}", headers=HEADERS)) as r:
        schema_body = r.read().decode("utf-8")

    schema = loads(schema_body)
    clean_schema_tree(schema)

    with open(p_args.output, "w", encoding="utf-8") as f:
        dump(schema, f, indent=2)
