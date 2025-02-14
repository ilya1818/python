import sqlite3
from tkinter import Canvas, Scrollbar, VERTICAL

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# Настройка базы данных
conn = sqlite3.connect("internet_shop.db")
cursor = conn.cursor()

# Создание таблиц
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id),
    UNIQUE(user_id, product_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    address TEXT,
    phone TEXT,
    payment_status TEXT DEFAULT 'Not Paid',
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()


# Основной класс приложения
class InternetShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интернет-магазин")
        self.root.geometry("800x600")
        self.current_user = None

        self.create_login_window()

    def create_login_window(self):
        """Окно входа в систему"""
        self.clear_window()
        ttk.Label(self.root, text="Добро пожаловать в Интернет-магазин", font=("Arial", 16)).pack(pady=20)

        ttk.Label(self.root, text="Логин:").pack()
        self.login_entry = ttk.Entry(self.root)
        self.login_entry.pack(pady=5)

        ttk.Label(self.root, text="Пароль:").pack()
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.root, text="Войти", command=self.authenticate, bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Регистрация", command=self.create_registration_window, bootstyle=INFO).pack()

    def create_registration_window(self):
        """Окно регистрации"""
        self.clear_window()
        ttk.Label(self.root, text="Регистрация нового пользователя", font=("Arial", 16)).pack(pady=20)

        ttk.Label(self.root, text="Логин:").pack()
        self.new_login_entry = ttk.Entry(self.root)
        self.new_login_entry.pack(pady=5)

        ttk.Label(self.root, text="Пароль:").pack()
        self.new_password_entry = ttk.Entry(self.root, show="*")
        self.new_password_entry.pack(pady=5)

        ttk.Label(self.root, text="Имя:").pack()
        self.new_name_entry = ttk.Entry(self.root)
        self.new_name_entry.pack(pady=5)

        ttk.Label(self.root, text="Адрес:").pack()
        self.new_address_entry = ttk.Entry(self.root)
        self.new_address_entry.pack(pady=5)

        ttk.Label(self.root, text="Телефон:").pack()
        self.new_phone_entry = ttk.Entry(self.root)
        self.new_phone_entry.pack(pady=5)

        ttk.Label(self.root, text="Email:").pack()
        self.new_email_entry = ttk.Entry(self.root)
        self.new_email_entry.pack(pady=5)

        ttk.Button(self.root, text="Зарегистрироваться", command=self.register_user, bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Назад", command=self.create_login_window, bootstyle=WARNING).pack()

    def authenticate(self):
        """Авторизация пользователя"""
        username = self.login_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            self.current_user = user
            if username == "admin":  # Проверка, если это admin
                self.create_admin_window()
            else:
                self.create_main_window()
        else:
            Messagebox.show_error("Неверный логин или пароль!", title="Ошибка")

    def create_admin_window(self):
        """Главное окно администратора"""
        self.clear_window()
        ttk.Label(self.root, text="Добро пожаловать, Администратор!", font=("Arial", 16)).pack(pady=20)

        ttk.Button(self.root, text="Список клиентов", command=self.show_users, bootstyle=PRIMARY).pack(pady=10)
        ttk.Button(self.root, text="Список товаров", command=self.show_catalog, bootstyle=INFO).pack(pady=10)
        ttk.Button(self.root, text="Список заказов", command=self.show_orders, bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Выход", command=self.create_login_window, bootstyle=DANGER).pack(pady=10)

    def show_users(self):
        """Отображение списка клиентов"""
        self.clear_window()
        ttk.Label(self.root, text="Список клиентов", font=("Arial", 16)).pack(pady=20)

        users = cursor.execute("SELECT * FROM users").fetchall()
        for user in users:
            frame = ttk.Frame(self.root, padding=10)
            frame.pack(fill=X, padx=10, pady=5)

            ttk.Label(frame, text=f"{user[3]} ({user[1]})", anchor=W).pack(side=LEFT, padx=5)
            ttk.Button(frame, text="Редактировать", command=lambda u=user: self.edit_user(u), bootstyle=SUCCESS).pack(
                side=RIGHT)

        ttk.Button(self.root, text="Назад", command=self.create_admin_window, bootstyle=WARNING).pack(pady=10)

    def edit_user(self, user):
        """Редактирование данных клиента"""
        self.clear_window()
        ttk.Label(self.root, text="Редактирование клиента", font=("Arial", 16)).pack(pady=20)

        ttk.Label(self.root, text="Имя:").pack()
        name_entry = ttk.Entry(self.root)
        name_entry.insert(0, user[3])
        name_entry.pack(pady=5)

        ttk.Label(self.root, text="Адрес:").pack()
        address_entry = ttk.Entry(self.root)
        address_entry.insert(0, user[4])
        address_entry.pack(pady=5)

        ttk.Label(self.root, text="Телефон:").pack()
        phone_entry = ttk.Entry(self.root)
        phone_entry.insert(0, user[5])
        phone_entry.pack(pady=5)

        ttk.Label(self.root, text="Email:").pack()
        email_entry = ttk.Entry(self.root)
        email_entry.insert(0, user[6])
        email_entry.pack(pady=5)

        ttk.Button(self.root, text="Сохранить",
                   command=lambda: self.save_user_edit(user[0], name_entry, address_entry, phone_entry, email_entry),
                   bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Назад", command=self.show_users, bootstyle=WARNING).pack(pady=10)

    def save_user_edit(self, user_id, name_entry, address_entry, phone_entry, email_entry):
        """Сохранение изменений данных клиента"""
        cursor.execute("""UPDATE users SET name = ?, address = ?, phone = ?, email = ? WHERE id = ?""",
                       (name_entry.get(), address_entry.get(), phone_entry.get(), email_entry.get(), user_id))
        conn.commit()
        Messagebox.show_info("Данные обновлены!", title="Успех")
        self.show_users()

    def show_catalog(self):
        """Отображение списка товаров с возможностью редактировать и добавлять новые товары"""
        self.clear_window()
        ttk.Label(self.root, text="Список товаров", font=("Arial", 16)).pack(pady=20)

        # Создаем контейнер для скроллинга
        canvas = Canvas(self.root)
        scroll_y = Scrollbar(self.root, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scroll_y.set)

        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Создаем фрейм для размещения товаров внутри канваса
        product_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=product_frame, anchor="nw")

        # Получаем список товаров из базы данных
        products = cursor.execute("SELECT * FROM products").fetchall()
        for product in products:
            frame = ttk.Frame(product_frame, padding=10)
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame, text=f"{product[1]} — {product[2]} руб. (В наличии: {product[3]})", anchor="w").pack(
                side="left", padx=5)
            ttk.Button(frame, text="Редактировать", command=lambda p=product: self.edit_product(p),
                       bootstyle="SUCCESS").pack(side="right")

        # Обновляем размер фрейма для корректного отображения скролла
        product_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Контейнер для кнопок "Назад" и "Добавить товар"
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", side="bottom", pady=10)  # Размещаем внизу

        # Кнопка "Назад"
        ttk.Button(bottom_frame, text="Назад", command=self.create_admin_window, bootstyle="WARNING").pack(side="left",
                                                                                                           padx=10)

        # Кнопка "Добавить товар"
        ttk.Button(bottom_frame, text="Добавить товар", command=self.add_product_window, bootstyle="SUCCESS").pack(
            side="right", padx=10)

    def add_product_window(self):
        """Окно для добавления нового товара"""
        print("Окно для добавления товара отображается")
        self.clear_window()
        ttk.Label(self.root, text="Добавить новый товар", font=("Arial", 16)).pack(pady=20)

        # Поля для ввода данных нового товара
        ttk.Label(self.root, text="Название:").pack()
        name_entry = ttk.Entry(self.root)
        name_entry.pack(pady=5)

        ttk.Label(self.root, text="Цена:").pack()
        price_entry = ttk.Entry(self.root)
        price_entry.pack(pady=5)

        ttk.Label(self.root, text="Количество:").pack()
        stock_entry = ttk.Entry(self.root)
        stock_entry.pack(pady=5)

        # Кнопка для сохранения товара
        ttk.Button(self.root, text="Сохранить",
                   command=lambda: self.save_new_product(name_entry, price_entry, stock_entry),
                   bootstyle="SUCCESS").pack(pady=10)

        # Кнопка "Назад" для возврата в список товаров
        ttk.Button(self.root, text="Назад", command=self.show_products, bootstyle="WARNING").pack(pady=10)

    def save_new_product(self, name_entry, price_entry, stock_entry):
        """Сохранение нового товара в базу данных"""
        name = name_entry.get()
        price = price_entry.get()
        stock = stock_entry.get()

        # Выполнение SQL запроса для добавления товара в базу данных
        cursor.execute("""INSERT INTO products (name, price, stock) VALUES (?, ?, ?)""", (name, price, stock))
        conn.commit()

        Messagebox.show_info("Товар добавлен!", title="Успех")
        self.show_products()  # Обновляем список товаров после добавления

    def edit_product(self, product):
        """Редактирование товара"""
        self.clear_window()
        ttk.Label(self.root, text="Редактирование товара", font=("Arial", 16)).pack(pady=20)

        ttk.Label(self.root, text="Название:").pack()
        name_entry = ttk.Entry(self.root)
        name_entry.insert(0, product[1])
        name_entry.pack(pady=5)

        ttk.Label(self.root, text="Цена:").pack()
        price_entry = ttk.Entry(self.root)
        price_entry.insert(0, product[2])
        price_entry.pack(pady=5)

        ttk.Label(self.root, text="Количество:").pack()
        stock_entry = ttk.Entry(self.root)
        stock_entry.insert(0, product[3])
        stock_entry.pack(pady=5)

        ttk.Button(self.root, text="Сохранить",
                   command=lambda: self.save_product_edit(product[0], name_entry, price_entry, stock_entry),
                   bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Назад", command=self.show_products, bootstyle=WARNING).pack(pady=10)

    def save_product_edit(self, product_id, name_entry, price_entry, stock_entry):
        """Сохранение изменений товара"""
        cursor.execute("""UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?""",
                       (name_entry.get(), price_entry.get(), stock_entry.get(), product_id))
        conn.commit()
        Messagebox.show_info("Товар обновлен!", title="Успех")
        self.show_products()

    def show_orders(self):
        """Отображение списка заказов клиентов с переводом статусов"""
        self.clear_window()
        ttk.Label(self.root, text="Список заказов", font=("Arial", 16)).pack(pady=20)

        orders = cursor.execute("""
            SELECT o.id, u.name, o.order_date, o.status 
            FROM orders o 
            JOIN users u ON o.user_id = u.id
        """).fetchall()

        for order in orders:
            translated_status = "В ожидании" if order[3] == "Pending" else "Подтвержден"
            frame = ttk.Frame(self.root, padding=10)
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame, text=f"Заказ {order[0]} от {order[1]} — {translated_status}", anchor="w").pack(side="left",
                                                                                                            padx=5)
            ttk.Button(frame, text="Изменить статус", command=lambda o=order: self.change_order_status(o),
                       bootstyle=SUCCESS).pack(side="right")

        ttk.Button(self.root, text="Назад", command=self.create_admin_window, bootstyle=WARNING).pack(pady=10)

    def change_order_status(self, order):
        """Изменение статуса заказа"""
        new_status = 'Подтвержден' if order[3] == 'Pending' else 'Pending'
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order[0]))
        conn.commit()
        Messagebox.show_info(f"Статус заказа изменен на {new_status}", title="Успех")
        self.show_orders()

    def register_user(self):
        """Регистрация нового пользователя"""
        username = self.new_login_entry.get()
        password = self.new_password_entry.get()
        name = self.new_name_entry.get()
        address = self.new_address_entry.get()
        phone = self.new_phone_entry.get()
        email = self.new_email_entry.get()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, name, address, phone, email) VALUES (?, ?, ?, ?, ?, ?)",
                (username, password, name, address, phone, email),
            )
            conn.commit()
            Messagebox.show_info("Регистрация прошла успешно!", title="Успех")
            self.create_login_window()
        except sqlite3.IntegrityError:
            Messagebox.show_error("Такой логин уже существует!", title="Ошибка")

    def create_main_window(self):
        """Главное окно интернет-магазина"""
        self.clear_window()
        ttk.Label(self.root, text=f"Добро пожаловать, {self.current_user[3]}!", font=("Arial", 16)).pack(pady=20)

        ttk.Button(self.root, text="Каталог товаров", command=self.show_products, bootstyle=PRIMARY).pack(pady=10)
        ttk.Button(self.root, text="Моя корзина", command=self.show_cart, bootstyle=INFO).pack(pady=10)
        ttk.Button(self.root, text="Мой профиль", command=self.show_profile, bootstyle=SUCCESS).pack(pady=10)
        ttk.Button(self.root, text="Выход", command=self.create_login_window, bootstyle=DANGER).pack(pady=10)

    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_products(self):
        """Отображение списка товаров с разным функционалом для администратора и пользователя"""
        self.clear_window()
        ttk.Label(self.root, text="Список товаров", font=("Arial", 16)).pack(pady=20)

        # Создаём рамку для Canvas и Scrollbar
        container = ttk.Frame(self.root)
        container.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Создаём Canvas
        canvas = Canvas(container)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Добавляем Scrollbar к Canvas
        scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Привязываем Scrollbar к Canvas
        canvas.configure(yscrollcommand=scrollbar.set)

        # Создаём рамку внутри Canvas для контента
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Функция для обновления размеров Canvas при изменении содержимого
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", on_frame_configure)

        # Заполняем список товаров
        products = cursor.execute("SELECT * FROM products").fetchall()
        for product in products:
            frame = ttk.Frame(content_frame, padding=10)
            frame.pack(fill=X, padx=10, pady=5)

            ttk.Label(frame, text=f"{product[1]} — {product[2]} руб. (В наличии: {product[3]})", anchor=W).pack(
                side=LEFT, padx=5)

            if self.current_user[1] == 'admin':
                # Администратор видит кнопку "Редактировать"
                ttk.Button(frame, text="Редактировать", command=lambda p=product: self.edit_product(p),
                           bootstyle="SUCCESS").pack(side=RIGHT)
            else:
                # Пользователь видит кнопку "Добавить в корзину"
                ttk.Button(frame, text="Добавить в корзину", command=lambda p=product: self.add_to_cart(p),
                           bootstyle="INFO").pack(side=RIGHT)

        # Контейнер для кнопки "Назад"
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", side="bottom", pady=10)  # Размещаем внизу

        # Кнопка "Назад" по центру
        ttk.Button(bottom_frame, text="Назад", command=self.create_main_window, bootstyle="WARNING").pack()

    def add_to_cart(self, product):
        """Добавление товара в корзину"""
        # Проверка наличия товара на складе
        if product[3] <= 0:
            Messagebox.show_error("Товар отсутствует на складе!", title="Ошибка")
            return

        print(f"Debug: stock decrease query for product_id={product[0]}, stock={product[3]}")

        try:
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, product_id) 
                DO UPDATE SET quantity = quantity + 1
            """, (self.current_user[0], product[0]))

            cursor.execute("UPDATE products SET stock = stock - 1 WHERE i = ?", (product[0],))
            conn.commit()

            Messagebox.show_info("Товар добавлен в корзину!", title="Успех")
        except sqlite3.Error as e:
            Messagebox.show_error(f"Ошибка: {e}", title="Ошибка")

    def show_cart(self):
        """Отображение корзины"""
        self.clear_window()

        ttk.Label(self.root, text="Моя корзина", font=("Arial", 16)).pack(pady=20)

        cart_items = cursor.execute("""
            SELECT c.id, p.name, p.price, c.quantity 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = ?
        """, (self.current_user[0],)).fetchall()

        total = 0
        for item in cart_items:
            total += item[2] * item[3]
            frame = ttk.Frame(self.root, padding=10)
            frame.pack(fill=X, padx=10, pady=5)
            ttk.Label(frame, text=f"{item[1]} — {item[2]} руб. x {item[3]} шт.", anchor=W).pack(side=LEFT, padx=5)

        if cart_items:
            ttk.Label(self.root, text=f"Итого: {total} руб.", font=("Arial", 14)).pack(pady=10)
            ttk.Button(self.root, text="Оформить заказ", command=self.place_order, bootstyle=SUCCESS).pack(pady=10)

        ttk.Button(self.root, text="На главную", command=self.create_main_window, bootstyle=WARNING).pack(pady=10)

    def place_order(self):
        """Оформление заказа"""
        # Получение товаров из корзины
        cart_items = cursor.execute("""
            SELECT p.name, c.quantity, p.price 
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        """, (self.current_user[0],)).fetchall()

        if not cart_items:
            Messagebox.show_error("Корзина пуста!", title="Ошибка")
            return

        # Рассчитать общую стоимость заказа
        total = sum(item[1] * item[2] for item in cart_items)

        # Получить данные пользователя для заказа
        address = self.current_user[4]
        phone = self.current_user[5]

        # Создать запись в таблице orders
        cursor.execute("""
            INSERT INTO orders (user_id, order_date, address, phone, status, payment_status)
            VALUES (?, DATE('now'), ?, ?, 'Pending', 'Not Paid')
        """, (self.current_user[0], address, phone))
        order_id = cursor.lastrowid

        # Удалить товары из корзины
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (self.current_user[0],))
        conn.commit()

        Messagebox.show_info(f"Заказ #{order_id} оформлен на сумму {total} руб!", title="Успех")

        # Очистить корзину на интерфейсе
        self.show_cart()

    def show_profile(self):
        """Показ информации о профиле пользователя"""
        self.clear_window()
        ttk.Label(self.root, text="Мой профиль", font=("Arial", 16)).pack(pady=20)

        info = [
            ("Логин", self.current_user[1]),
            ("Имя", self.current_user[3]),
            ("Адрес", self.current_user[4]),
            ("Телефон", self.current_user[5]),
            ("Email", self.current_user[6]),
        ]

        for label, value in info:
            ttk.Label(self.root, text=f"{label}: {value}", font=("Arial", 12)).pack(pady=5)

        ttk.Button(self.root, text="Назад", command=self.create_main_window, bootstyle=WARNING).pack(pady=10)


if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = InternetShopApp(root)
    root.mainloop()
