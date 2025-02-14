MOD = 998244353

# Чтение n и k с проверкой диапазонов
n, k = map(int, input().split())

# Проверяем, что n и k соответствуют ограничениям
if not (2 <= n <= 2 * 10 ** 5) or not (1 <= k <= 300):
    raise ValueError("Значения n и k выходят за пределы допустимых значений")

# Чтение массива a
a = list(map(int, input().split()))

# Проверяем, что все элементы массива a соответствуют ограничениям
if any(not (1 <= x <= 10 ** 8) for x in a):
    raise ValueError("Некоторые элементы массива a выходят за пределы допустимых значений")

# Считаем сумму всех элементов массива
total_sum = sum(a) % MOD

# Для каждого p от 1 до k рассчитываем f(p)
for p in range(1, k + 1):
    # Массив для хранения степеней элементов
    sum_of_powers = 0

    # Считаем суммы всех пар
    for i in range(n):
        for j in range(i + 1, n):
            # Сумма пары
            pair_sum = (a[i] + a[j]) % MOD
            # Возводим сумму в степень p
            sum_of_powers = (sum_of_powers + pow(pair_sum, p, MOD)) % MOD

    # Выводим результат для f(p)
    print(sum_of_powers)
