import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Подключение к SQL Server
connection_string = (
    r"Driver={SQL Server};"
    r"Server=DESKTOP-INMG3JQ\SQLEXPRESS;"
    r"Database=Компания;"
    r"Trusted_Connection=yes;"
)

# Основное окно
root = tk.Tk()
root.title("Управление компанией")
root.geometry("1400x600")
root.configure(bg="#F4E8D3")
root.iconbitmap("icon.ico")

# Основной контейнер для карточек
cards_frame = tk.Frame(root, bg="#F4E8D3")
cards_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Переменная для хранения текущего режима отображения
current_view = tk.StringVar(value="Партнеры")

# Контейнер для прокрутки карточек
canvas = tk.Canvas(root, bg="#F4E8D3")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Обертывание карточек в канвас
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Основной контейнер для карточек на канвасе
cards_frame = tk.Frame(canvas, bg="#F4E8D3")
canvas.create_window((0, 0), window=cards_frame, anchor="nw")

# Установим фиксированную ширину для карточек
card_width = 200


# Функция для создания карточки партнера
def create_partner_card(partner):
    card = tk.Frame(cards_frame, bg="#F4E8D3", width=card_width, height=150, bd=1, relief="solid", padx=10, pady=10)

    # Заголовок
    label = tk.Label(card, text=partner["Наименование партнера"], font=("Arial", 12, "bold"))
    label.pack()

    # Другие данные
    label_type = tk.Label(card, text=f"Тип: {partner['Тип партнера']}", font=("Arial", 10))
    label_type.pack()
    label_director = tk.Label(card, text=f"Директор: {partner['Директор']}", font=("Arial", 10))
    label_director.pack()
    label_phone = tk.Label(card, text=f"Телефон: {partner['Телефон партнера']}", font=("Arial", 10))
    label_phone.pack()
    label_rating = tk.Label(card, text=f"Рейтинг: {partner['Рейтинг']}", font=("Arial", 10))
    label_rating.pack()
    label_discount = tk.Label(card, text=f"Скидка: {partner['Скидка']}%", font=("Arial", 10))
    label_discount.pack()

    # Расположение карточки
    card.pack(side="top", padx=5, pady=5, fill="x")


# Функция для обновления данных в зависимости от режима
def refresh_data():
    """Обновляет данные в зависимости от выбранного режима."""
    # Скрыть/показать кнопки
    if current_view.get() == "Партнеры":
        add_button.pack(pady=5)
        edit_button.pack(pady=5)
    else:
        add_button.pack_forget()
        edit_button.pack_forget()

    # Удаляем старые карточки
    for widget in cards_frame.winfo_children():
        widget.destroy()

    # В зависимости от выбранного режима показываем нужные карточки
    if current_view.get() == "Партнеры":
        partners = get_partners()
        for partner in partners:
            create_partner_card(partner)
    elif current_view.get() == "Продукция":
        products = get_products()
        for product in products:
            create_product_card(product)

    # Обновление области прокрутки
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# Функция для извлечения партнеров из базы данных
def get_partners():
    """Извлекает данные о партнерах из базы данных."""
    partners = []
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.[Наименование партнера], p.[Тип партнера], p.[Директор], p.[Телефон партнера], p.[Рейтинг], 
                       SUM(pp.[Количество продукции]) AS TotalSales
                FROM Партнеры p
                LEFT JOIN Партнеры_продукция pp ON p.[Наименование партнера] = pp.[Наименование партнера]
                GROUP BY p.[Наименование партнера], p.[Тип партнера], p.[Директор], p.[Телефон партнера], p.[Рейтинг]
            """)
            for row in cursor.fetchall():
                total_sales = row[5] if row[5] else 0
                discount = calculate_discount(total_sales)
                rating = int(row[4]) if row[4] is not None else 0

                partners.append({
                    "Наименование партнера": row[0],
                    "Тип партнера": row[1],
                    "Директор": row[2],
                    "Телефон партнера": row[3],
                    "Рейтинг": rating,
                    "Скидка": discount,
                    "TotalSales": total_sales,
                })
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при подключении к базе данных: {e}")
    return partners


def get_products():
    """Извлекает данные о продукции из базы данных."""
    products = []
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT [Продукция], [Размер упаковки], [Себестоимость]
                FROM [Продукция_инфо]
            """)
            for row in cursor.fetchall():
                # Проверка, является ли значение себестоимости числом
                cost = row[2] if isinstance(row[2], (int, float)) else None

                products.append({
                    "Продукция": row[0],
                    "Размер упаковки": row[1],
                    "Себестоимость": cost,
                })
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при подключении к базе данных: {e}")
    return products


def calculate_discount(total_sales):
    """Рассчитывает скидку на основе объема продаж."""
    if total_sales >= 300000:
        return 15
    elif total_sales >= 50000:
        return 10
    elif total_sales >= 10000:
        return 5
    return 0


def create_partner_card(partner):
    """Создает карточку с информацией о партнере и чекбоксом для выбора."""
    card = tk.Frame(cards_frame, bg="#FFFFFF", bd=1, relief="solid", cursor="hand2")
    card.pack(fill="x", padx=5, pady=5)

    # Информация внутри карточки
    title = f"{partner['Тип партнера']} | {partner['Наименование партнера']}"
    tk.Label(card, text=title, font=("Arial", 14, "bold"), anchor="w", bg="#FFFFFF").pack(fill="x", pady=(5, 0))
    tk.Label(card, text=f"Директор: {partner['Директор']}", anchor="w", bg="#FFFFFF").pack(fill="x")
    tk.Label(card, text=f"Телефон: {partner['Телефон партнера']}", anchor="w", bg="#FFFFFF").pack(fill="x")
    tk.Label(card, text=f"Рейтинг: {partner['Рейтинг']}", anchor="w", bg="#FFFFFF").pack(fill="x")
    tk.Label(card, text=f"Скидка: {partner['Скидка']}%", font=("Arial", 12, "italic"), anchor="e", bg="#FFFFFF").pack(
        fill="x", pady=(0, 5))

    # Чекбокс для выбора партнера
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(card, variable=var, command=lambda: select_partner(card, var))
    checkbox.pack(side="right", padx=10)

    # Присваиваем переменную карточке для дальнейшего использования
    card.partner = partner

    # Кнопка для отображения количества продаж
    sales_button = tk.Button(card, text="Продажи", command=lambda: show_sales_info(partner))
    sales_button.pack(side="bottom", padx=10, pady=5)


def select_partner(card, var):
    """Выбирает партнера при изменении состояния чекбокса."""
    global selected_partner

    if var.get():  # Если чекбокс активен
        # Сбрасываем выделение с предыдущего партнера
        if selected_partner:
            selected_partner.configure(bg="#FFFFFF")

        # Выделяем текущую карточку
        card.configure(bg="#D3F3D3")
        selected_partner = card  # Сохраняем выбранную карточку
    else:
        # Если чекбокс снят, сбрасываем выделение
        card.configure(bg="#FFFFFF")
        selected_partner = None


def show_sales_info(partner):
    """Открывает окно с информацией о продажах партнера."""
    sales_window = tk.Toplevel(root)
    sales_window.title(f"Продажи партнера: {partner['Наименование партнера']}")
    sales_window.geometry("400x300")

    sales_label = tk.Label(sales_window, text=f"Общее количество продаж: {partner['TotalSales']}", font=("Arial", 12))
    sales_label.pack(pady=20)

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT [Продукция], [Наименование партнера], [Количество продукции], [Дата продажи]
                FROM Партнеры_продукция
                WHERE [Наименование партнера] = ?
            """, (partner['Наименование партнера'],))
            sales_data = cursor.fetchall()

            if sales_data:
                for sale in sales_data:
                    sale_text = f"{sale[0]} - {sale[1]} шт, {sale[2]}"
                    tk.Label(sales_window, text=sale_text).pack(anchor="w")
            else:
                tk.Label(sales_window, text="Нет данных о продажах.").pack(pady=10)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при получении данных о продажах: {e}")


def open_edit_window():
    """Открывает окно для изменения данных выбранного партнера."""
    if selected_partner:
        partner = selected_partner.partner
        edit_window = tk.Toplevel(root)
        edit_window.title(f"Редактировать партнера: {partner['Наименование партнера']}")
        edit_window.geometry("400x300")

        # Поля для редактирования информации о партнере
        tk.Label(edit_window, text="Директор:").pack(pady=5)
        director_entry = tk.Entry(edit_window)
        director_entry.insert(0, partner["Директор"])
        director_entry.pack(pady=5)

        tk.Label(edit_window, text="Телефон:").pack(pady=5)
        phone_entry = tk.Entry(edit_window)
        phone_entry.insert(0, partner["Телефон партнера"])
        phone_entry.pack(pady=5)

        tk.Label(edit_window, text="Рейтинг:").pack(pady=5)
        rating_entry = tk.Entry(edit_window)
        rating_entry.insert(0, partner["Рейтинг"])
        rating_entry.pack(pady=5)

        # Кнопка для сохранения изменений
        def save_changes():
            new_director = director_entry.get()
            new_phone = phone_entry.get()
            new_rating = rating_entry.get()

            # Сохраняем изменения в базе данных
            update_partner_in_db(partner['Наименование партнера'], new_director, new_phone, new_rating)
            messagebox.showinfo("Изменения сохранены",
                                f"Информация о партнере {partner['Наименование партнера']} успешно изменена.")
            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Сохранить изменения", command=save_changes)
        save_button.pack(pady=10)

    else:
        messagebox.showwarning("Ошибка", "Пожалуйста, выберите партнера для редактирования.")


def update_partner_in_db(partner_name, director, phone, rating):
    """Обновляет данные партнера в базе данных."""
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            # Проверяем и преобразуем рейтинг в правильный формат (целое число или десятичное число)
            if isinstance(rating, str):
                # Проверяем, если рейтинг строка, пытаемся преобразовать его в число
                if rating.replace('.', '', 1).isdigit():  # Проверка, если это числовое значение
                    rating = float(rating) if '.' in rating else int(rating)
                else:
                    rating = 0  # Если не число, ставим 0

            cursor.execute("""
                UPDATE Партнеры
                SET [Директор] = ?, [Телефон партнера] = ?, [Рейтинг] = ?
                WHERE [Наименование партнера] = ?
            """, (director, phone, rating, partner_name))
            conn.commit()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при обновлении данных партнера: {e}")


def open_add_window():
    """Открывает окно для добавления нового партнера."""
    add_window = tk.Toplevel(root)
    add_window.title("Добавить партнера")
    add_window.geometry("400x300")

    # Поля для ввода информации о новом партнере
    tk.Label(add_window, text="Наименование партнера:").pack(pady=5)
    name_entry = tk.Entry(add_window)
    name_entry.pack(pady=5)

    tk.Label(add_window, text="Тип партнера:").pack(pady=5)
    type_entry = tk.Entry(add_window)
    type_entry.pack(pady=5)

    tk.Label(add_window, text="Директор:").pack(pady=5)
    director_entry = tk.Entry(add_window)
    director_entry.pack(pady=5)

    tk.Label(add_window, text="Телефон:").pack(pady=5)
    phone_entry = tk.Entry(add_window)
    phone_entry.pack(pady=5)

    tk.Label(add_window, text="Рейтинг:").pack(pady=5)
    rating_entry = tk.Entry(add_window)
    rating_entry.pack(pady=5)

    # Кнопка для сохранения нового партнера
    def save_new_partner():
        name = name_entry.get()
        type_ = type_entry.get()
        director = director_entry.get()
        phone = phone_entry.get()
        rating = rating_entry.get()

        # Сохраняем нового партнера в базе данных
        add_partner_to_db(name, type_, director, phone, rating)
        messagebox.showinfo("Новый партнер добавлен", f"Партнер {name} успешно добавлен.")
        add_window.destroy()
        refresh_data()

    tk.Button(add_window, text="Добавить партнера", command=save_new_partner).pack(pady=10)


def add_partner_to_db(name, type_, director, phone, rating):
    """Добавляет нового партнера в базу данных."""
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Партнеры ([Наименование партнера], [Тип партнера], Директор, [Телефон партнера], Рейтинг)
                VALUES (?, ?, ?, ?, ?)
            """, (name, type_, director, phone, rating))
            conn.commit()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при добавлении партнера: {e}")


def create_product_card(product):
    """Создает карточку с информацией о продукции."""
    card = tk.Frame(cards_frame, bg="#FFFFFF", bd=1, relief="solid")
    card.pack(fill="x", padx=5, pady=5)

    # Информация внутри карточки
    tk.Label(card, text=product["Продукция"], font=("Arial", 14, "bold"), bg="#FFFFFF").pack(fill="x", pady=5)
    tk.Label(card, text=f"Размер упаковки: {product['Размер упаковки']} ", anchor="w", bg="#FFFFFF").pack(fill="x")
    tk.Label(card, text=f"Себестоимость: {product['Себестоимость']}", anchor="w", bg="#FFFFFF").pack(fill="x")


# Верхняя часть управления
header_frame = tk.Frame(root, bg="#F4E8D3")
header_frame.pack(side="top", fill="x", pady=10)

# Заголовок компании
title_label = tk.Label(header_frame, text="Компания мастер полов", font=("Arial", 24, "bold"), bg="#F4E8D3")
title_label.pack()

# Выбор режима
view_menu = ttk.Combobox(header_frame, textvariable=current_view, values=["Партнеры", "Продукция"], state="readonly")
view_menu.pack(pady=5)
view_menu.bind("<<ComboboxSelected>>", lambda e: refresh_data())

# Добавление изображения (логотип компании)
try:
    logo_image = Image.open("icon.png")  # Замените "icon.png" на путь к вашему изображению
    logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Измените размер по необходимости
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(header_frame, image=logo_photo, bg="#F4E8D3")
    logo_label.pack(pady=5)
except Exception as e:
    messagebox.showwarning("Ошибка изображения", f"Не удалось загрузить изображение: {e}")

# Кнопки управления
control_frame = tk.Frame(root, bg="#F4E8D3")
control_frame.pack(side="right", fill="y", padx=40, pady=5)

# Кнопки управления
control_frame = tk.Frame(root, bg="#F4E8D3")
control_frame.pack(side="right", fill="y", padx=40, pady=5)

refresh_button = tk.Button(control_frame, text="Обновить данные", command=refresh_data)
refresh_button.pack(pady=5)

edit_button = tk.Button(control_frame, text="Редактировать партнера", command=open_edit_window)
edit_button.pack(pady=5)

add_button = tk.Button(control_frame, text="Добавить партнера", command=open_add_window)
add_button.pack(pady=5)

# Загрузка данных при старте
refresh_data()

# Запуск приложения
root.mainloop()
