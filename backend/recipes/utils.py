from hashids import Hashids
from django.conf import settings


hashids = Hashids(
    salt=settings.SECRET_KEY,
    min_length=6,
)


def encode_recipe_id(recipe_id):
    return hashids.encode(recipe_id)


def decode_recipe_id(code):
    decoded = hashids.decode(code)

    if not decoded:
        return None

    return decoded[0]
