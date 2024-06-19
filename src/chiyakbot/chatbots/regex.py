import re

escape_for_md_compile = re.compile("[.+\\-()!,<>\\|}{/:=&_]")
escape_for_marketprice_compile = re.compile("[.+\\-,}{/:=&]")
escape_for_marketprice_name_compile = re.compile("[)(]")
calc_p = re.compile("^=[0-9+\-*/%!^( )]+")
is_uuid = re.compile("^[0-9a-f]{32}$")
is_url = re.compile(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def escape_for_md(text, isPickup):
    result = ""
    if isPickup:
        result = escape_for_md_compile.sub("\\\\\\g<0>", text)
    else:
        result = escape_for_marketprice_compile.sub("\\\\\\g<0>", text)
    return result
