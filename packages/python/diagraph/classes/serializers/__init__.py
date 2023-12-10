from .v1 import deserialize, serialize

SERIALIZERS = {
    "1": {
        "serialize": serialize,
        "deserialize": deserialize,
    },
}
