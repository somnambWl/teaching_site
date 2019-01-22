
def convert(from_unit, to_unit):
    from_unit = deepcopy(from_unit)
    if from_unit.name != to_unit.name:
        factor = from_unit.SI_value / to_unit.SI_value
        from_unit._value = from_unit._value * factor
    return from_unit._value
