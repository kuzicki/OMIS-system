def is_primitive_root(g, P):
    # Множество для хранения всех уникальных значений g^i mod P
    seen = set()

    # Проходим по всем степеням от 1 до P-1
    for i in range(1, P):
        # Вычисляем g^i mod P
        result = pow(g, i, P)
        
        # Если результат уже встречался, то g не является примитивным элементом
        if result in seen:
            return False
        seen.add(result)

    # Проверяем, что все значения от 1 до P-1 присутствуют
    return len(seen) == P - 1

P = 23  # Пример простого числа
g = 5   # Кандидат на примитивный элемент

if is_primitive_root(g, P):
    print(f"{g} является примитивным элементом поля GF({P})")
else:
    print(f"{g} не является примитивным элементом поля GF({P})")
