# rooster_price = 5
# hen_price = 3
# chicken_price = 1 / 3
# total_money = 100
# max_rooster = int(total_money / rooster_price)
# max_hen = int(total_money / hen_price)
#
# for rooster_count in range(max_rooster + 1):
#     for hen_count in range(max_hen + 1):
#         chicken_count = total_money - rooster_count - hen_count
#         if rooster_count * rooster_price + hen_count * hen_price + chicken_count * chicken_price == 100:
#             print(f'Solution: roosters = {rooster_count}, hens = {hen_count}, chickens = {chicken_count}')
x = float(input())

def calculate_e(x):
    result = 0
    factorial = 1
    for i in range(100):
        result += (x ** i) / factorial
        factorial *= (i + 1)

    return result
print(f"e: {calculate_e(1)}")
print(f"e^0.5: {calculate_e(0.5)}")
print(f"e^x: {calculate_e(x)}, where x = {x}")
