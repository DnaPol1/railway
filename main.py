import tkinter as tk
from tkinter import messagebox
import psycopg2
from tkinter import ttk

def connect():
    try:
        conn = psycopg2.connect(dbname='railway', user='postgres', password='Hexrf', host='localhost')
        return conn
    except:
        print('Can`t establish connection to database')

def authenticate_and_set_role(login, password):
    conn = connect()
    if not  conn:
        return
    try:
        with conn.cursor() as cursor:
            # Проверяем логин и пароль
            cursor.execute("""
                    SELECT role FROM users 
                    WHERE login = %s AND password = %s
                """, (login, password))
            result = cursor.fetchone()
            if not result:
                tk.messagebox.showinfo('Ошибка', 'Неверный логин или пароль')
                print("Authentication failed: Invalid login or password")
                return
            user_role = result[0]  # Получаем роль из результата запроса
            # Выполняем SET ROLE для активации роли
            cursor.execute(f"SET ROLE {user_role}_role;")
            conn.commit()  # Подтверждаем изменение роли
            return user_role
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def on_login_click():
    login = name_text.get()
    password = password_text.get()
    user_role = authenticate_and_set_role(login, password)
    if user_role:
        window.destroy()
        if user_role == 'user':
            open_user_window()
        elif user_role == 'seller':
            open_seller_window()
        elif user_role == 'manager':
            open_manager_window()

def on_search_click(arrival_text, depart_text, tree):
    # Получаем названия станций из полей ввода
    departure_station_name = arrival_text.get()
    arrival_station_name = depart_text.get()
    # Получаем данные с помощью функции
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT * FROM get_routes_by_station_names(%s, %s)
            """, (departure_station_name, arrival_station_name))
    # Получаем все строки из результата запроса
    rows = cursor.fetchall()
    # Очищаем таблицу перед добавлением новых данных
    for item in tree.get_children():
        tree.delete(item)
    # Вставляем новые данные в таблицу
    for row in rows:
        tree.insert("", tk.END, values=row)


def on_search_click_price(arrival_text, depart_text, tree):
    # Получаем названия станций из полей ввода
    departure_station_name = arrival_text.get()
    arrival_station_name = depart_text.get()
    # Получаем данные с помощью функции
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT * FROM get_routes_by_station_names(%s, %s)
            """, (departure_station_name, arrival_station_name))
    # Получаем все строки из результата запроса
    route = cursor.fetchone()
    # Очищаем таблицу перед добавлением новых данных
    if route:
        route_number, departure_time, arrival_time = route;
        cursor.execute("""
                    SELECT adult_price, child_price
                    FROM get_or_create_price(%s, %s, %s);
                """, (route_number, departure_station_name, arrival_station_name))
        # Получаем результат
        result = cursor.fetchone()

        if result:
            adult_price, child_price = result;
    tree.insert("", "end", values=(route_number, departure_station_name, arrival_station_name,
                                   departure_time, arrival_time, adult_price, child_price));

def open_user_window():
    user_window = tk.Tk()
    user_window.title('Железные дороги | Пользователь')
    user_window.geometry('800x600')
    frame = tk.Frame(
        user_window,
        padx=10,
        pady=10
    )
    frame.pack(expand=True)
    arrival = tk.Label(
        frame,
        text="Введите станцию отбытия:"
    )
    arrival.grid(row=1, column=1)
    depart = tk.Label(
        frame,
        text="Введите станцию прибытия:"
    )
    depart.grid(row=2, column=1)
    arrival_text = tk.Entry(
        frame
    )
    arrival_text.grid(row=1, column=2)
    depart_text = tk.Entry(
        frame
    )
    depart_text.grid(row=2, column=2)
    search = tk.Button(
        frame,
        text="Поиск",
        command=lambda: on_search_click(arrival_text, depart_text, tree)
    )
    search.grid(row=4, column=2)
    tree = ttk.Treeview(frame, columns=("Route Number", "Departure Time", "Arrival Time"), show="headings")
    tree.heading("Route Number", text="Номер маршрута")
    tree.heading("Departure Time", text="Время отбытия")
    tree.heading("Arrival Time", text="Время прибытия")
    tree.grid(row=5, column=1, columnspan=2, pady=10)
    user_window.mainloop()

def open_seller_window():
    seller_window = tk.Tk()
    seller_window.title('Железные дороги | Кассир')
    seller_window.geometry('800x600')
    frame = tk.Frame(
        seller_window,
        padx=10,
        pady=10
    )
    frame.pack(expand=True)
    arrival = tk.Label(
        frame,
        text="Введите станцию отбытия:"
    )
    arrival.grid(row=1, column=1)
    depart = tk.Label(
        frame,
        text="Введите станцию прибытия:"
    )
    depart.grid(row=2, column=1)
    arrival_text = tk.Entry(
        frame
    )
    arrival_text.grid(row=1, column=2)
    depart_text = tk.Entry(
        frame
    )
    depart_text.grid(row=2, column=2)
    search = tk.Button(
        frame,
        text="Поиск",
        command=lambda: on_search_click_price(arrival_text, depart_text, tree)
    )
    search.grid(row=4, column=2)
    tree = ttk.Treeview(frame, columns=("Route Number", "Departure Station", "Arrival Station",
                                        "Departure Time", "Arrival Time", "Adult Price", "Child Price"),
                        show="headings")
    tree.heading("Route Number", text="Номер маршрута")
    tree.heading("Departure Station", text="Станция отбытия")
    tree.heading("Arrival Station", text="Станция прибытия")
    tree.heading("Departure Time", text="Время отбытия")
    tree.heading("Arrival Time", text="Время прибытия")
    tree.heading("Adult Price", text="Цена взрослого")
    tree.heading("Child Price", text="Цена детского")
    tree.column("Route Number", width=105, anchor='center')
    tree.column("Departure Station", width=105, anchor='center')
    tree.column("Arrival Station", width=110, anchor='center')
    tree.column("Departure Time", width=95, anchor='center')
    tree.column("Arrival Time", width=95, anchor='center')
    tree.column("Adult Price", width=95, anchor='center')
    tree.column("Child Price", width=95, anchor='center')
    tree.grid(row=6, column=1, columnspan=2, pady=10)
    seller_window.mainloop()

def open_manager_window():
    manager_window = tk.Tk()
    manager_window.title('Железные дороги | Руководство')
    manager_window.geometry('800x600')
    frame = tk.Frame(
        manager_window,
        padx=10,
        pady=10
    )
    frame.pack(expand=True)
    arrival = tk.Label(
        frame,
        text="Введите станцию отбытия:"
    )
    arrival.grid(row=1, column=1)
    depart = tk.Label(
        frame,
        text="Введите станцию прибытия:"
    )
    depart.grid(row=2, column=1)
    arrival_text = tk.Entry(
        frame
    )
    arrival_text.grid(row=1, column=2)
    depart_text = tk.Entry(
        frame
    )
    depart_text.grid(row=2, column=2)
    search = tk.Button(
        frame,
        text="Поиск",
        command=lambda: on_search_click_price(arrival_text, depart_text, tree)
    )
    search.grid(row=4, column=2)
    tree = ttk.Treeview(frame, columns=("Route Number", "Departure Station", "Arrival Station",
                                        "Departure Time", "Arrival Time", "Adult Price", "Child Price"),
                        show="headings")
    tree.heading("Route Number", text="Номер маршрута")
    tree.heading("Departure Station", text="Станция отбытия")
    tree.heading("Arrival Station", text="Станция прибытия")
    tree.heading("Departure Time", text="Время отбытия")
    tree.heading("Arrival Time", text="Время прибытия")
    tree.heading("Adult Price", text="Цена взрослого")
    tree.heading("Child Price", text="Цена детского")
    tree.column("Route Number", width=105, anchor='center')
    tree.column("Departure Station", width=105, anchor='center')
    tree.column("Arrival Station", width=110, anchor='center')
    tree.column("Departure Time", width=95, anchor='center')
    tree.column("Arrival Time", width=95, anchor='center')
    tree.column("Adult Price", width=95, anchor='center')
    tree.column("Child Price", width=95, anchor='center')
    tree.grid(row=6, column=1, columnspan=2, pady=10)
    manager_window.mainloop()

window = tk.Tk() #создание окна приложения
window.title("Железные дороги") #название приложения
window.geometry('800x600') #размер окна
frame = tk.Frame( #создание виджета
    window, #окно для размещения
    padx = 10, #отступ по горизонтали
    pady = 10 #отступ по вертикали
)
frame.pack(expand=True) #Не забываем позиционировать виджет в окне. Здесь используется метод pack. С помощью свойства expand=True указываем, что Frame заполняет весь контейнер, созданный для него.
welcome = tk.Label(
    frame,
    text="Добро пожаловать!"
)
welcome.grid(row=1, column=1)
#вход в приложение
name = tk.Label(
    frame,
    text="Введите логин:"
)
name.grid(row=2, column=1)
password = tk.Label(
    frame,
    text="Введите пароль:"
)
password.grid(row=3, column=1)
name_text = tk.Entry(
    frame
)
name_text.grid(row=2, column=2)
password_text = tk.Entry (
    frame,
    show = '*'
)
password_text.grid(row=3,column=2)
login = tk.Button(
    frame,
    text = "Войти",
    command=on_login_click
)
login.grid(row=4,column=2)
window.mainloop() #запуск цикла событий, чтобы приложение не закрывалось само. должно быть в конце