import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Импортируем необходимые модули Pillow
import psycopg2


# Подключение к базе данных PostgresSQL
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="Техникум",
            user="postgres",
            password="1",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Ошибка подключения",
                             "Не удалось подключиться к базе данных. Проверьте настройки подключения.")
        return None


# Получение списка таблиц в базе данных
def get_tables(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
        return tables
    except Exception as e:
        messagebox.showerror("Ошибка получения таблиц",
                             "Не удалось получить список таблиц. Пожалуйста, попробуйте позже.")
        return []


# Получение данных из таблицы
def get_table_data(conn, table_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
        return column_names, rows
    except Exception as e:
        messagebox.showerror("Ошибка получения данных",
                             f"Не удалось получить данные из таблицы {table_name}. Пожалуйста, попробуйте позже.")
        return [], []


# Поиск информации по ФИО преподавателя
def search_by_teacher(conn, teacher_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.Номер_преподавателя, p.ФИО_преподавателя, d.Дисциплина, r.День, r.Пара, g.Группа, k.Номер_кабинета
                FROM Преподаватели p
                JOIN Дисциплины d ON p.Номер_дисциплины = d.Номер_дисциплины
                LEFT JOIN Расписание r ON p.Номер_преподавателя = r.Номер_преподавателя
                LEFT JOIN Группы g ON r.Группа = g.Группа
                LEFT JOIN Кабинеты k ON r.Номер_кабинета = k.Номер_кабинета
                WHERE p.ФИО_преподавателя LIKE %s
            """, (f"%{teacher_name}%",))
            rows = cursor.fetchall()
            column_names = ["Номер преподавателя", "ФИО преподавателя", "Дисциплина", "День", "Пара", "Группа",
                            "Номер кабинета"]
        return column_names, rows
    except Exception as e:
        messagebox.showerror("Ошибка поиска",
                             "Не удалось найти информацию о преподавателе. Пожалуйста, проверьте введенные данные и попробуйте снова.")
        return [], []


# Поиск информации по группе
def search_by_group(conn, group_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT g.Группа, g.Количество_человек, r.День, r.Пара, d.Дисциплина, p.ФИО_преподавателя, k.Номер_кабинета
                FROM Группы g
                LEFT JOIN Расписание r ON g.Группа = r.Группа
                LEFT JOIN Дисциплины d ON r.Номер_дисциплины = d.Номер_дисциплины
                LEFT JOIN Преподаватели p ON r.Номер_преподавателя = p.Номер_преподавателя
                LEFT JOIN Кабинеты k ON r.Номер_кабинета = k.Номер_кабинета
                WHERE g.Группа LIKE %s
            """, (f"%{group_name}%",))
            rows = cursor.fetchall()
            column_names = ["Группа", "Количество человек", "День", "Пара", "Дисциплина", "ФИО преподавателя",
                            "Номер кабинета"]
        return column_names, rows
    except Exception as e:
        messagebox.showerror("Ошибка поиска",
                             "Не удалось найти информацию о группе. Пожалуйста, проверьте введенные данные и попробуйте снова.")
        return [], []


# Проверка на конфликты при добавлении/редактировании расписания
def check_conflicts(conn, day, pair, group=None, teacher=None, room=None, current_id=None):
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT COUNT(*) 
                FROM Расписание r
                WHERE r.День = %s AND r.Пара = %s
            """
            params = [day, pair]

            if group:
                query += " AND r.Группа = %s"
                params.append(group)
            if teacher:
                query += " AND r.Номер_преподавателя = %s"
                params.append(teacher)
            if room:
                query += " AND r.Номер_кабинета = %s"
                params.append(room)

            if current_id:
                query += " AND r.Номер_расписания != %s"
                params.append(current_id)

            cursor.execute(query, tuple(params))
            count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        messagebox.showerror("Ошибка проверки конфликтов",
                             "Не удалось проверить конфликты. Пожалуйста, попробуйте позже.")
        return False


# Диалоговое окно для редактирования записи
class EditRecordDialog(tk.Toplevel):
    def __init__(self, parent, table_name, current_values, conn):
        super().__init__(parent)
        self.title("Редактирование записи")
        self.result = None
        self.conn = conn

        columns, _ = get_table_data(conn, table_name)

        self.entries = []
        for i, col in enumerate(columns):
            label = tk.Label(self, text=col)
            label.grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self)
            entry.insert(0, current_values[i])
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        button = tk.Button(self, text="Сохранить", command=self.save)
        button.grid(row=len(columns), column=0, columnspan=2, pady=10)

    def save(self):
        self.result = [entry.get() for entry in self.entries]
        self.destroy()


# Диалоговое окно для добавления записи
class AddRecordDialog(tk.Toplevel):
    def __init__(self, parent, table_name, conn):
        super().__init__(parent)
        self.title("Добавление записи")
        self.result = None
        self.conn = conn

        columns, _ = get_table_data(conn, table_name)

        self.entries = []
        for i, col in enumerate(columns):
            label = tk.Label(self, text=col)
            label.grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        button = tk.Button(self, text="Добавить", command=self.add)
        button.grid(row=len(columns), column=0, columnspan=2, pady=10)

    def add(self):
        self.result = [entry.get() for entry in self.entries]
        self.destroy()


# Диалоговое окно для поиска по ФИО преподавателя
class SearchTeacherDialog(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.title("Поиск по ФИО преподавателя")
        self.result = None

        label = tk.Label(self, text="Введите ФИО преподавателя:")
        label.pack(padx=10, pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(padx=10, pady=5)

        button = tk.Button(self, text="Поиск", command=self.search)
        button.pack(padx=10, pady=10)

    def search(self):
        self.result = self.entry.get()
        self.destroy()


# Диалоговое окно для поиска по группе
class SearchGroupDialog(tk.Toplevel):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.title("Поиск по группе")
        self.result = None

        label = tk.Label(self, text="Введите название группы:")
        label.pack(padx=10, pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(padx=10, pady=5)

        button = tk.Button(self, text="Поиск", command=self.search)
        button.pack(padx=10, pady=10)

    def search(self):
        self.result = self.entry.get()
        self.destroy()


# Главное окно приложения
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Работа с базой данных PostgreSQL")
        self.geometry("1000x600")

        self.conn = connect_to_db()
        if not self.conn:
            self.destroy()
            return

        # Главное меню
        self.main_menu = tk.Menu(self)
        self.config(menu=self.main_menu)

        # Вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_tabs()

        # Кнопки редактирования, удаления и добавления записей
        self.edit_button = tk.Button(self, text="Редактирование выбранной записи", command=self.edit_record)
        self.delete_button = tk.Button(self, text="Удаление записи", command=self.delete_record)
        self.add_button = tk.Button(self, text="Добавление записи", command=self.add_record)

        self.search_teacher_button = tk.Button(self, text="Поиск по ФИО преподавателя", command=self.search_teacher)
        self.search_group_button = tk.Button(self, text="Поиск по группе", command=self.search_group)

        self.edit_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.search_teacher_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.search_group_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.current_tree = None  # Добавляем переменную для хранения текущего Treeview
        self.current_table_name = None  # Добавляем переменную для хранения текущей таблицы

        # Добавляем изображение в главное окно
        self.add_image()

    def create_tabs(self):
        tables = get_tables(self.conn)
        for table in tables:
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=table)
            tree = self.create_table_view(frame, table)
            frame.tree = tree  # Сохраняем ссылку на Treeview в фрейме

        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        current_tab = self.notebook.index('current')
        self.current_table_name = self.notebook.tab(current_tab, "text")
        self.current_tree = self.notebook.nametowidget(self.notebook.select()).tree
        self.refresh_table()

    def create_table_view(self, frame, table_name):
        columns, rows = get_table_data(self.conn, table_name)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)
        tree.bind('<<TreeviewSelect>>', lambda event: self.on_tree_select(tree))

        return tree

    def on_tree_select(self, tree):
        selected_item = tree.selection()
        if selected_item:
            self.selected_item = selected_item
            self.selected_values = tree.item(selected_item)['values']
        else:
            self.selected_item = None
            self.selected_values = None

    def edit_record(self):
        if not hasattr(self, 'selected_item') or not self.selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования.")
            return

        dialog = EditRecordDialog(self, self.current_table_name, self.selected_values, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            update_query = f"UPDATE {self.current_table_name} SET "
            set_clauses = []
            for i, value in enumerate(dialog.result):
                set_clauses.append(f"{self.current_tree['columns'][i]} = %s")
            update_query += ", ".join(set_clauses)
            update_query += f" WHERE {self.current_tree['columns'][0]} = %s"

            primary_key = self.selected_values[0]

            day_index = self.current_tree['columns'].index('День') if 'День' in self.current_tree['columns'] else None
            pair_index = self.current_tree['columns'].index('Пара') if 'Пара' in self.current_tree['columns'] else None
            group_index = self.current_tree['columns'].index('Группа') if 'Группа' in self.current_tree[
                'columns'] else None
            teacher_index = self.current_tree['columns'].index('Номер_преподавателя') if 'Номер_преподавателя' in \
                                                                                         self.current_tree[
                                                                                             'columns'] else None
            room_index = self.current_tree['columns'].index('Номер_кабинета') if 'Номер_кабинета' in self.current_tree[
                'columns'] else None

            day = dialog.result[day_index] if day_index is not None else None
            pair = dialog.result[pair_index] if pair_index is not None else None
            group = dialog.result[group_index] if group_index is not None else None
            teacher = dialog.result[teacher_index] if teacher_index is not None else None
            room = dialog.result[room_index] if room_index is not None else None

            if day and pair and (group or teacher or room):
                if check_conflicts(self.conn, day, pair, group, teacher, room, primary_key):
                    messagebox.showerror("Ошибка редактирования записи",
                                         "Произошел конфликт расписания. Пожалуйста, измените параметры.")
                    return

            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(update_query, (*dialog.result, primary_key))
                    self.conn.commit()
            except Exception as e:
                messagebox.showerror("Ошибка редактирования записи",
                                     "Не удалось обновить запись. Пожалуйста, проверьте введенные данные и попробуйте снова.")
                return

            self.refresh_table()

    def delete_record(self):
        if not hasattr(self, 'selected_item') or not self.selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
            return

        primary_key = self.selected_values[0]
        delete_query = f"DELETE FROM {self.current_table_name} WHERE {self.current_tree['columns'][0]} = %s"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(delete_query, (primary_key,))
                self.conn.commit()
        except Exception as e:
            messagebox.showerror("Ошибка удаления записи", "Не удалось удалить запись. Пожалуйста, попробуйте позже.")
            return

        self.refresh_table()

    def add_record(self):
        dialog = AddRecordDialog(self, self.current_table_name, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            if any(value == '' for value in dialog.result):
                messagebox.showerror("Ошибка добавления записи",
                                     "Не все поля заполнены. Пожалуйста, заполните все поля и попробуйте снова.")
                return

            columns, _ = get_table_data(self.conn, self.current_table_name)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {self.current_table_name} VALUES ({placeholders})"

            day_index = columns.index('День') if 'День' in columns else None
            pair_index = columns.index('Пара') if 'Пара' in columns else None
            group_index = columns.index('Группа') if 'Группа' in columns else None
            teacher_index = columns.index('Номер_преподавателя') if 'Номер_преподавателя' in columns else None
            room_index = columns.index('Номер_кабинета') if 'Номер_кабинета' in columns else None

            day = dialog.result[day_index] if day_index is not None else None
            pair = dialog.result[pair_index] if pair_index is not None else None
            group = dialog.result[group_index] if group_index is not None else None
            teacher = dialog.result[teacher_index] if teacher_index is not None else None
            room = dialog.result[room_index] if room_index is not None else None

            if day and pair and (group or teacher or room):
                if check_conflicts(self.conn, day, pair, group, teacher, room):
                    messagebox.showerror("Ошибка добавления записи",
                                         "Произошел конфликт расписания. Пожалуйста, измените параметры.")
                    return

            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(insert_query, dialog.result)
                    self.conn.commit()
            except Exception as e:
                messagebox.showerror("Ошибка добавления записи",
                                     "Не удалось добавить запись. Пожалуйста, проверьте введенные данные и попробуйте снова.")
                return

            self.refresh_table()

    def refresh_table(self):
        if self.current_tree:
            self.current_tree.delete(*self.current_tree.get_children())
            columns, rows = get_table_data(self.conn, self.current_table_name)
            for row in rows:
                self.current_tree.insert("", tk.END, values=row)

    def search_teacher(self):
        dialog = SearchTeacherDialog(self, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            columns, rows = search_by_teacher(self.conn, dialog.result)
            if not rows:
                messagebox.showinfo("Результаты поиска", "По вашему запросу ничего не найдено.")
            else:
                self.display_search_results(columns, rows)

    def search_group(self):
        dialog = SearchGroupDialog(self, self.conn)
        self.wait_window(dialog)

        if dialog.result:
            columns, rows = search_by_group(self.conn, dialog.result)
            if not rows:
                messagebox.showinfo("Результаты поиска", "По вашему запросу ничего не найдено.")
            else:
                self.display_search_results(columns, rows)

    def display_search_results(self, columns, rows):
        result_window = tk.Toplevel(self)
        result_window.title("Результаты поиска")

        tree = ttk.Treeview(result_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

    def add_image(self):
        # Загружаем изображение с помощью PIL
        image_path = "1.png"  # Здесь замените на ваш путь к изображению
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Изменяем размер изображения по необходимости
            photo = ImageTk.PhotoImage(img)

            # Создаем метку для отображения изображения
            self.image_label = tk.Label(self, image=photo)
            self.image_label.image = photo  # Сохраняем ссылку на изображение, чтобы оно не было удалено сборщиком мусора
            self.image_label.pack(side=tk.RIGHT, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Ошибка загрузки изображения", f"Не удалось загрузить изображение: {e}")


# Создание Git
if __name__ == "__main__":
    app = App()
    app.mainloop()
