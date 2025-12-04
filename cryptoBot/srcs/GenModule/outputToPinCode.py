def transform_conditions(conditions):
    transformed_conditions = []
    for condition in conditions:
        condition = [str(elem).lower() for elem in condition]
        if condition[2] == '<=':
            transformed_conditions.append(f"{condition[0]}_{condition[1]} <= {condition[3]}_{condition[4]}")
        elif condition[2] == '>=':
            transformed_conditions.append(f"{condition[0]}_{condition[1]} >= {condition[3]}_{condition[4]}")
        elif condition[2] == '>':
            transformed_conditions.append(f"{condition[0]}_{condition[1]} > {condition[3]}_{condition[4]}")
        elif condition[2] == '<':
            transformed_conditions.append(f"{condition[0]}_{condition[1]} < {condition[3]}_{condition[4]}")
    return " and ".join(transformed_conditions)

p = [
    [['High', 7, '<=', 'Open', 4], ['High', 4, '>', 'High', 8], ['Open', 3, '<', 'Open', 2]],
    [['Close', 8, '<=', 'Open', 3], ['Close', 7, '<=', 'High', 3], ['Close', 5, '<', 'Open', 6]]
]

p2 = [
    [['Open', 4, '>=', 'Close', 1], ['High', 4, '>=', 'Low', 9], ['Low', 7, '>', 'High', 4], ['Open', 5, '<', 'High', 8], ['High', 5, '>', 'High', 0]],
    [['Low', 6, '<=', 'Low', 6], ['Close', 7, '<=', 'High', 3], ['Low', 1, '<=', 'High', 9], ['High', 9, '<=', 'Close', 3], ['Close', 2, '>=', 'Low', 3]]
]


conditions = p2[1]
result = transform_conditions(conditions)
print(result)
