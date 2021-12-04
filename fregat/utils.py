from django.utils.text import slugify
from hashlib import md5
from pathlib import Path
import time
from unidecode import unidecode


def to_float(val, default=None):
    result = default

    if isinstance(val, (str, bytes)):
        val = val.replace(',', '.')

    if val is not None:
        try:
            result = float(val)
        except (ValueError, TypeError, KeyError):
            result = default

    return result


def to_int(val, default=None):
    result = default

    if isinstance(val, (str, bytes)):
        val = val.replace(',', '.')

    if val is not None:
        try:
            result = int(val)
        except (ValueError, TypeError, KeyError):
            result = default

    return result


def transliterate(line):
    return slugify(unidecode(line))


def get_unique_upload_path(instance, original_name, keep_name=False):
    solt = str(time.time()) + original_name
    path_hash = md5(solt.encode('utf8')).hexdigest()

    path = Path(original_name)
    file_name = path.name if keep_name else path_hash + path.suffix

    n = [1, 2, 4, 8, 16, ]

    return Path(
        instance._meta.app_label,
        instance._meta.model_name,
        *[path_hash[sum(n[:i]):sum(n[:i+1])] for i in range(len(n))],
        path_hash,
        file_name
    )


def get_upload_path_with_name_keeping(instance, filename):
    return get_unique_upload_path(instance, filename, True)


def get_upload_path_without_name_keeping(instance, filename):
    return get_unique_upload_path(instance, filename, False)
