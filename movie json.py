import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("800x500")
        
        # Файл для хранения данных
        self.data_file = "movies.json"
        self.movies = []
        
        # Загрузка данных из JSON
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # === Фрейм для ввода данных ===
        input_frame = LabelFrame(self.root, text="Информация о фильме", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Название
        Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Жанр
        Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.genre_entry = Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Год выпуска
        Label(input_frame, text="Год выпуска:").grid(row=1, column=0, sticky="w")
        self.year_entry = Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Рейтинг
        Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", padx=(20,0))
        self.rating_entry = Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Кнопка добавления
        self.add_btn = Button(input_frame, text="Добавить фильм", command=self.add_movie, bg="lightgreen")
        self.add_btn.grid(row=1, column=4, padx=20, pady=5)
        
        # === Фрейм для фильтрации ===
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        Label(filter_frame, text="Фильтр по жанру:").pack(side="left", padx=5)
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.pack(side="left", padx=5)
        
        Label(filter_frame, text="Фильтр по году:").pack(side="left", padx=5)
        self.year_filter = Entry(filter_frame, width=10)
        self.year_filter.pack(side="left", padx=5)
        
        Button(filter_frame, text="Применить фильтр", command=self.refresh_table).pack(side="left", padx=10)
        Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).pack(side="left", padx=5)
        
        # === Таблица для отображения фильмов ===
        table_frame = Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создание таблицы с прокруткой
        scrollbar = Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(table_frame, columns=("title", "genre", "year", "rating"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # Настройка заголовков
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")
        
        self.tree.column("title", width=250)
        self.tree.column("genre", width=150)
        self.tree.column("year", width=80)
        self.tree.column("rating", width=80)
        
        self.tree.pack(fill="both", expand=True)
        
        # Кнопка удаления выбранного фильма
        Button(self.root, text="Удалить выбранный фильм", command=self.delete_movie, bg="lightcoral").pack(pady=5)
    
    def validate_movie(self, title, genre, year_str, rating_str):
        """Проверка корректности введённых данных"""
        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не могут быть пустыми!")
            return False
        
        try:
            year = int(year_str)
            if year < 1888 or year > 2026:  # Первый фильм появился в 1888 году
                messagebox.showerror("Ошибка", "Год должен быть между 1888 и 2026!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return False
        
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return False
        
        return True
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        if self.validate_movie(title, genre, year, rating):
            movie = {
                "title": title,
                "genre": genre,
                "year": int(year),
                "rating": float(rating)
            }
            self.movies.append(movie)
            self.save_data()
            self.refresh_table()
            
            # Очистка полей
            self.title_entry.delete(0, END)
            self.genre_entry.delete(0, END)
            self.year_entry.delete(0, END)
            self.rating_entry.delete(0, END)
            
            messagebox.showinfo("Успех", f"Фильм '{title}' добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return
        
        # Получаем название фильма из выделенной строки
        item = self.tree.item(selected[0])
        title = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{title}'?"):
            # Удаляем из списка
            self.movies = [m for m in self.movies if m['title'] != title]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Фильм удалён!")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        genre_filter = self.genre_filter.get().strip().lower()
        year_filter = self.year_filter.get().strip()
        
        # Фильтрация
        filtered_movies = self.movies
        if genre_filter:
            filtered_movies = [m for m in filtered_movies if genre_filter in m['genre'].lower()]
        if year_filter:
            try:
                year = int(year_filter)
                filtered_movies = [m for m in filtered_movies if m['year'] == year]
            except ValueError:
                pass  # Если фильтр не число, игнорируем
        
        # Заполнение таблицы
        for movie in filtered_movies:
            self.tree.insert("", END, values=(movie['title'], movie['genre'], movie['year'], movie['rating']))
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.genre_filter.delete(0, END)
        self.year_filter.delete(0, END)
        self.refresh_table()
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
            except:
                self.movies = []
        else:
            # Пример данных для демонстрации
            self.movies = [
                {"title": "Побег из Шоушенка", "genre": "Драма", "year": 1994, "rating": 9.3},
                {"title": "Крёстный отец", "genre": "Криминал", "year": 1972, "rating": 9.2},
                {"title": "Тёмный рыцарь", "genre": "Боевик", "year": 2008, "rating": 9.0},
                {"title": "Криминальное чтиво", "genre": "Криминал", "year": 1994, "rating": 8.9}
            ]
            self.save_data()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.movies, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = Tk()
    app = MovieLibrary(root)
    root.mainloop()