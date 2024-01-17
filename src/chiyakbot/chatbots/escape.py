import re

escape_for_md_compile = re.compile("[.+\\-()!,<>\\|}{/:=&_]")
escape_for_marketprice_compile = re.compile("[.+\\-,}{/:=&]")
escape_for_marketprice_name_compile = re.compile("[)(]")


def escape_for_md(text, isPickup):
    result = ""
    if isPickup:
        result = escape_for_md_compile.sub("\\\\\\g<0>", text)
    else:
        result = escape_for_marketprice_compile.sub("\\\\\\g<0>", text)
    return result
