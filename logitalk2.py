import threading
from socket import *
from customtkinter import *

# Головне вікно чату, яке наслідується від CTk (CustomTkinter)
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')  # Задаємо розмір вікна
        self.title("nogard chat")
        self.label = None  # Попереднє оголошення елемента метки (пізніше додається в меню)

        # ========== СТВОРЕННЯ ВИСУВНОГО МЕНЮ ==========
        self.menu_frame = CTkFrame(self, width=30, height=300 , fg_color = "yellowgreen")
        self.menu_frame.pack_propagate(False)  # Вимикає автоматичне масштабування віджетів всередині
        self.menu_frame.place(x=0, y=0)  # Розташування меню

        self.is_show_menu = False  # Чи відкрите меню
        self.speed_animate_menu = -5  # Швидкість анімації (негативна — закриття, позитивна — відкриття)

        # Кнопка розкриття/закриття меню
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30 , fg_color = "green")
        self.btn.place(x=0, y=0)

        # ========== ОСНОВНЕ ПОЛЕ ЧАТУ ==========
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable' , fg_color = 'light green' , text_color = "dark green")  # Текстове поле лише для читання
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', fg_color=("olive") , height=40 , text_color = "drak green" , placeholder_text_color= "dark green")
        self.message_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message , fg_color=("green") , state='disable')
        self.send_button.place(x=0, y=0)

        # ========== ІМ'Я КОРИСТУВАЧА ТА ПІДКЛЮЧЕННЯ ДО СЕРВЕРА ==========
        self.username = 'nogard'  # Ім'я за замовчуванням (можна змінити з меню)

        try:
            # Створення сокета для підключення до сервера
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))  # Підключення до локального сервера на порту 8080

            # Надсилання повідомлення про приєднання
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))

            # Запуск окремого потоку для прослуховування вхідних повідомлень
            threading.Thread(target=self.recv_message, daemon=True).start()

        except Exception as e:
            # Якщо не вдалося підключитися
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        # Адаптація інтерфейсу до розміру вікна (щоб все підлаштовувалось динамічно)
        self.adaptive_ui()

    # ========== ПЕРЕМИКАННЯ МЕНЮ (АНІМАЦІЯ) ==========
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            # Додавання віджетів меню: мітка та поле введення для імені
            self.label = CTkLabel(self.menu_frame, text='Імʼя' )
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame , fg_color = "limegreen")
            self.entry.pack()
            self.label_theme = CTkOptionMenu(self.menu_frame, values=['Темна', 'Темна'], command=self.change_theme , fg_color= "darkgoldenrod" , text_color = "dark green")
            self.label_theme.pack(side='bottom', pady=20)

    # ========== АНІМАЦІЯ МЕНЮ ==========
    def show_menu(self):
        # Змінюємо ширину меню поступово, створюючи анімацію
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)

        # Відкриття меню — доки ширина не досягне 200 пікселів
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        # Закриття меню — доки ширина не менше 40
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    # ========== АДАПТИВНЕ РОЗТАШУВАННЯ ЕЛЕМЕНТІВ ==========
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())

        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)

        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)

        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

        # Через кожні 50 мс оновлюється розташування (на випадок зміни розміру або анімації меню)
        self.after(50, self.adaptive_ui)

    # ========== ДОДАВАННЯ ПОВІДОМЛЕННЯ В ПОЛЕ ЧАТУ ==========
    def add_message(self, text):
        self.chat_field.configure(state='normal')  # Дозволяємо редагування, щоб вставити текст
        self.chat_field.insert(END, 'Я: ' + text + '\n')
        self.chat_field.configure(state='disable')  # Знову блокуємо редагування

    # ========== ВІДПРАВКА ПОВІДОМЛЕННЯ НА СЕРВЕР ==========
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)  # Очищаємо поле введення

    # ========== ПРИЙОМ ПОВІДОМЛЕНЬ ВІД СЕРВЕРА ==========
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                # Розбиваємо за символом нового рядка
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    # ========== ОБРОБКА ВХІДНОГО ПОВІДОМЛЕННЯ ==========
    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        # Текстове повідомлення
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")

        # Повідомлення з зображенням (за протоколом)
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")

        # Інші типи повідомлень
        else:
            self.add_message(line)

    def change_theme(self, value):
        if value == 'Темна':  # Dark|темна
            set_appearance_mode('dark')
        else:
            set_appearance_mode('dark')

# Запуск програми
win = MainWindow()
win.mainloop()