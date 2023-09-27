from argparse import ArgumentParser
from urllib.request import Request, urlopen
from re import compile
from json import loads, dump

HEADERS = {"User-Agent": "Mozilla/5.0"}

LINK_PATTERN = compile(r'<a href="([a-z0-9/]+)">TMDB API - v3</a>')


def infer_schema_type(node: any) -> dict[str, any]:
    if isinstance(node, int):
        return {"type": "integer", "example": node}
    elif isinstance(node, str):
        return {"type": "string", "example": node}
    elif isinstance(node, float):
        return {"type": "number", "example": node}
    elif isinstance(node, list):
        return {"type": "array", "items": infer_schema_type(node[0])}
    elif isinstance(node, dict):
        return {"type": "object", "properties": {k: infer_schema_type(v) for k, v in node.items()}}

    raise Exception(f"Could not infer schema type of {node}")


def unescape_json(v: str, item_path: list[str] = []) -> dict[str, any]:
    if len(v) > 2 and (v.startswith("{}") or v.startswith("[]")):  # check malformed JSON example value
        if item_path:
            print(f"fixed malformed escaped JSON, path: {'.'.join(item_path)}")

        v = v[2:]

    return loads(v)


def clean_schema_tree(node: list | dict[str, any], path: list[str] = []):
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

                            print(f"fixed duplicate property {k1} -> {clean_key}, path: {'.'.join([*item_path, k1])}")

                        keys.add(clean_key)
                elif (k == "vote_average" or k == "rating") and ("type" not in v or v["type"] == "integer"):
                    # check vote type mismatch
                    v["type"] = "number"
                    v["nullable"] = True

                    print(f"fixed vote-related property type integer -> number, nullable, path: {'.'.join(item_path)}")
                elif k.endswith("_path") or k == "iso_639_1" or k == "adult":
                    # check non-null type
                    if "type" not in v:
                        v["type"] = "string"
                    v["nullable"] = True

                    print(f"fixed non-null property type, path: {'.'.join(item_path)}")
                elif k == "application/json" and "examples" in v and "schema" not in v:  # check missing schema
                    example_value = v["examples"]["Result"]["value"]
                    is_escaped_json = (isinstance(example_value, str) and
                                       ((example_value.startswith("{") and example_value.endswith("}"))
                                        or (example_value.startswith("[") and example_value.endswith("]"))))

                    v["schema"] = infer_schema_type(unescape_json(example_value) if is_escaped_json else example_value)
                    print(f"fixed missing schema, path: {'.'.join(item_path)}")

                clean_schema_tree(v, path=item_path)
            elif isinstance(v, list):
                clean_schema_tree(v, path=item_path)
            elif k == "default" and v is None:  # check null default
                node["nullable"] = True

                print(f"fixed null default, path: {'.'.join(item_path)}")
            elif item_path[-1] == "value" and item_path[-3] == "examples" and isinstance(v, str):
                # check escaped JSON example value in path .examples.{anything}.value
                if (v.startswith("{") and v.endswith("}")) or (v.startswith("[") and v.endswith("]")):
                    node[k] = unescape_json(v, item_path=item_path)

                    print(f"fixed escaped example, path: {'.'.join(item_path)}")
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
