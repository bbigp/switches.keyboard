def format_with_tolerance(value):
    base_value, tolerance, unit = value
    if base_value is None or base_value == '':
        return f'-{unit}'
    elif tolerance is None or tolerance == '':
        return f'{base_value}{unit}'
    else:
        return f'{base_value}{tolerance}{unit}'

def format_studio_with_manufacturer(value):
    studio, manufacturer = value
    if studio and manufacturer:
        if studio == manufacturer:
            return f'{studio}'
        else:
            return f'{studio} | {manufacturer}'
    elif studio or manufacturer:
        return f'{studio}{manufacturer}'
    else:
        return ''