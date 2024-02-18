
from django.db.models.fields.files import ImageField


def modify_input_for_multiple_files(key_name, key_value, image, image_name="image"):
    dictionary = {}
    dictionary[key_name] = key_value
    dictionary[image_name] = image
    return dictionary
