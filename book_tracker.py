import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        
        # Данные
        self.books = []
        self.data_file = "books.json"
        
        # Загрузка сохраненных данных
        self.load_data()
        
        # Создание GUI
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = LabelFrame(self.root, text="Добавить новую книгу", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Поля ввода
        Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w")
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w")
        self.author_entry = Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)
        
        Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w")
        self.genre_entry = Entry(input_frame, width=20)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)
        
        Label(input_frame, text="Количество страниц:").grid(row=1, column=2, sticky="w")
        self.pages_entry = Entry(input_frame, width=10)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = Button(input_frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        self.add_button.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Рамка для фильтрации
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5, pady=5)
        
        Label(filter_frame, text="Фильтр по страницам (больше):").grid(row=0, column=2, sticky="w")
        self.pages_filter = Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5, pady=5)
        
        self.filter_button = Button(filter_frame, text="Применить фильтр", command=self.apply_filter, bg="lightblue")
        self.filter_button.grid(row=0, column=4, padx=10, pady=5)
        
        self.reset_button = Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter, bg="lightgray")
        self.reset_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Рамка для таблицы
        table_frame = Frame(self.root)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Таблица
        columns = ("Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Настройка заголовков
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Кнопки управления
        button_frame = Frame(self.root)
        button_frame.pack(pady=10)
        
        self.delete_button = Button(button_frame, text="Удалить выбранную книгу", command=self.delete_book, bg="salmon")
        self.delete_button.pack(side=LEFT, padx=5)
        
        self.save_button = Button(button_frame, text="Сохранить в JSON", command=self.save_to_json, bg="lightyellow")
        self.save_button.pack(side=LEFT, padx=5)
    
    def add_book(self):
        # Проверка корректности ввода
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return
        
        # Добавление книги
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        
        # Очистка полей
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)
        
        # Сохранение и обновление
        self.save_to_json()
        self.refresh_table()
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")
    
    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return
        
        # Получаем название книги из выделенной строки
        item = self.tree.item(selected[0])
        title_to_delete = item['values'][0]
        
        # Удаляем из списка
        self.books = [book for book in self.books if book['title'] != title_to_delete]
        
        # Сохраняем и обновляем
        self.save_to_json()
        self.refresh_table()
        messagebox.showinfo("Успех", f"Книга '{title_to_delete}' удалена!")
    
    def apply_filter(self):
        genre_filter = self.genre_filter.get().strip().lower()
        pages_filter = self.pages_filter.get().strip()
        
        filtered_books = self.books.copy()
        
        # Фильтр по жанру
        if genre_filter:
            filtered_books = [book for book in filtered_books if genre_filter in book['genre'].lower()]
        
        # Фильтр по страницам
        if pages_filter:
            try:
                pages_min = int(pages_filter)
                filtered_books = [book for book in filtered_books if book['pages'] > pages_min]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр по страницам должен быть числом!")
                return
        
        self.update_table(filtered_books)
    
    def reset_filter(self):
        self.genre_filter.delete(0, END)
        self.pages_filter.delete(0, END)
        self.refresh_table()
    
    def refresh_table(self):
        self.update_table(self.books)
    
    def update_table(self, books_list):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем таблицу
        for book in books_list:
            self.tree.insert("", END, values=(book['title'], book['author'], book['genre'], book['pages']))
    
    def save_to_json(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
            except:
                self.books = []
        else:
            self.books = []

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()
