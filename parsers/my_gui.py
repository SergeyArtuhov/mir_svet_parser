import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import threading
from config import URL, HEADERS
from moytok import create_session, login, search_product_by_article

def window_gui():
    root = tk.Tk()
    app = ParserApp(root)
    
    style = ttk.Style()
    style.configure("TButton", padding=6)
    style.configure("TLabel", padding=6)
    
    root.mainloop()
    
    return app

class ParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер артикулов")
        self.root.geometry("800x600")
        self.stop_parsing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель (20%)
        left_frame = tk.Frame(main_frame, width=0.2*800)  # 20% от 800px = 160px
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)  # фиксирует ширину

        # Правая панель (80%)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.start_btn = ttk.Button(
            left_frame,
            text="Начать парсинг",
            command=self.start_parsing
        )
        self.start_btn.pack(pady=5, fill=tk.X, padx=5)

        self.file_btn = ttk.Button(
            left_frame,
            text="Выбрать файл Excel",
            command=self.select_file
        )
        self.file_btn.pack(pady=5, fill=tk.X, padx=5)

        self.export_btn = ttk.Button(
        left_frame,
        text="Экспорт в Excel",
        command=self.export_to_excel,
        state=tk.DISABLED
        )
        self.export_btn.pack(pady=5, fill=tk.X, padx=5)
# Прогресс бар
        self.progress = ttk.Progressbar(
        left_frame,
        orient=tk.HORIZONTAL,
        mode='determinate',
        length=150
        )
        self.progress.pack(pady=10, fill=tk.X, padx=5)

        self.progress_label = ttk.Label(
        left_frame,
        text="Готов к работе",
        anchor='center'
        )
        self.progress_label.pack(fill=tk.X, padx=5)
#
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = ttk.Label(
            left_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor='w'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.output_area = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=80
        )
        self.output_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def export_to_excel(self):
        if not self.parsed_data:
            self.status_var.set("Нет данных для экспорта")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Сохранить как"
        )

        if not file_path:
            return

        try:
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Парсинг артикулов"

            ws.append(["Артикул", "Цена"])

            for item in self.parsed_data:
                ws.append(item)

            wb.save(file_path)
            self.status_var.set(f"Данные сохранены в {file_path}")
            self.update_output(f"\nДанные экспортированы в: {file_path}\n")
        except Exception as e:
            self.status_var.set("Ошибка при экспорте")
            self.update_output(f"\nОшибка при экспорте: {str(e)}\n")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.status_var.set(f"Выбран файл: {file_path}")
            self.file_path = file_path 
    
    def start_parsing(self):
        if self.start_btn["text"] == "Отменить парсинг":
            self.stop_parsing = True
            self.status_var.set("Остановка парсинга...")
            return
        
        if not hasattr(self, 'file_path') or not self.file_path:
            self.status_var.set("Сначала выберите файл!")
            return

        self.stop_parsing = False
        self.start_btn.config(text="Отменить парсинг", state=tk.NORMAL)
        self.status_var.set("Парсинг запущен...")
        self.output_area.insert(tk.END, "=== Начало работы ===\n")

        thread = threading.Thread(target=self.run_parser, daemon=True)
        thread.start()
    
    def run_parser(self):
        try:
            if not hasattr(self, 'file_path') or not self.file_path:
                self.update_output("Файл не выбран!\n")
                return

            headers = HEADERS
            url = URL.get(1)["site"]
            login_url = f"{url}index.php?route=account/login"
            search_url = f"{url}index.php?route=product/search&search="
            login_data = URL.get(1)["data"]

            session = create_session()

            if login(session, login_url, login_data, headers, self):
                self.update_output("Авторизация успешна\n")
                search_product_by_article(session, search_url, self, self.file_path)
            else:
                self.update_output("Ошибка авторизации\n")
        except Exception as e:
            self.update_output(f"Ошибка: {str(e)}\n")
        finally:
            self.root.after(0, self.on_parsing_finished)

    
    def update_output(self, text):
        self.root.after(0, lambda: self.output_area.insert(tk.END, text))
        self.root.after(0, lambda: self.output_area.see(tk.END))
    
    def on_parsing_finished(self):
        self.start_btn.config(text="Начать парсинг", state=tk.NORMAL)
        if self.parsed_data:
            self.export_btn.config(state=tk.NORMAL)
            self.status_var.set("Готов к работе (есть данные для экспорта)")
        else:
            self.status_var.set("Готов к работе (нет данных для экспорта)")
        self.update_output("=== Работа завершена ===\n")
