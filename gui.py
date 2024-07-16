import customtkinter
import dbs
import webbrowser

db = dbs.DatabaseManager('./hbr.db')

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


root = customtkinter.CTk()
root.title('Habr News (Python)')
root.geometry('1400x800')
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure((2, 3), weight=0)
root.grid_rowconfigure((0, 1, 2), weight=1)
links = []


frame = customtkinter.CTkFrame(root, width=140, corner_radius=0)
frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
frame.grid_rowconfigure(4, weight=1)


tabview = customtkinter.CTkTabview(frame, width=250)
tabview.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
tabview.add("Search")
tabview.add("Add_news")
tabview.tab("Search").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
tabview.tab("Add_news").grid_columnconfigure(0, weight=1)


sframe = customtkinter.CTkScrollableFrame(
    master=tabview.tab('Search'),
    height=500,
    width=300,
    corner_radius=10)
sframe.grid(sticky="nsew", row=3, column=0, padx=20, pady=20)


entry = customtkinter.CTkEntry(tabview.tab('Search'), placeholder_text="Введи")
entry.grid(row=1, column=0, padx=(20, 20), pady=(30, 20), sticky="nsew", columnspan=2)

button_1_search = customtkinter.CTkButton(tabview.tab('Search'), text="GO!", command=lambda: (sframe_clear(), show_news(entry.get())))
button_1_search.grid(row=2, column=0, padx=20, pady=10)

button_2_search = customtkinter.CTkButton(tabview.tab('Search'), text="Clear", command=lambda: links.clear())
button_2_search.grid(row=4, column=0, padx=20, pady=10)


"""button_1_add = customtkinter.CTkButton(tabview.tab('Add_news'), text="GO!", command=lambda: )
button_1_add.grid(row=2, column=0, padx=20, pady=10)

button_2_add = customtkinter.CTkButton(tabview.tab('Add_news'), text="Clear", command=lambda: links.clear())
button_2_add.grid(row=4, column=0, padx=20, pady=10)"""


def prt(url):
    text: str = db.fetchone('SELECT body FROM news WHERE link = ?', (url,))
    textbox = customtkinter.CTkTextbox(root, border_width=3, height=700, font=('Times', 20))
    textbox.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
    textbox.grid_rowconfigure(4, weight=1)
    textbox.insert('0.0', *text)
    label = customtkinter.CTkLabel(root, text=url, font=('Times', 25))
    label.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="sw")
    label.grid_rowconfigure(4, weight=1)
    label.bind("<Button-1>", lambda event: webbrowser.open_new_tab(url))
    label.bind("<Enter>", lambda event: label.configure(font=('Times', 25, "underline"), cursor="hand2"))
    label.bind("<Leave>", lambda event: label.configure(font=('Times', 25), cursor="arrow"))


def show_news(title_searh: str):
    k = 0
    data = db.fetchall('SELECT title, link FROM news')
    src = {x: v for x, v in data}
    for i, v in src.items():
        if title_searh.lower() in i.lower():
            if v in links:
                continue
            else:
                if k == 20:
                    break
                bt = customtkinter.CTkButton(
                    master=sframe,
                    text=i,
                    command=lambda url=v: prt(url),
                    width=20,
                    height=20,
                    anchor='left')
                bt.pack()
                links.append(v)
                k += 1


def sframe_clear():
    for button in sframe.winfo_children():
        button.destroy()


if __name__ == "__main__":
    root.mainloop()
    show_news()
