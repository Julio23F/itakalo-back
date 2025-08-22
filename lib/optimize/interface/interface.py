"""
Fichier: interface.py

Ce fichier contient le code nécessaire pour créer et gérer l'interface utilisateur de l'application.
L'interface est conçue en utilisant la bibliothèque Tkinter de Python et inclut plusieurs fonctionnalités
pour faciliter la manipulation et la visualisation des données, telles que la sélection de fichiers,
la décompression et l'affichage des détails.

Auteur : Robin Lasserye
Date : 15/04/2023
Version : 1
"""
import os
import sys
import os.path
import tkinter as tk
from PIL import ImageTk
from style import *
from custom_window import CustomWindow
import json
from tkinter import filedialog
import zipfile
import shutil
import subprocess
from threading import Thread
import threading
from datetime import datetime
import psutil
from random import random
import re
import unidecode

list_of_windows = []
optimization_is_launched = False


def get_absolute_path(local_path):
    """
    Obtient le chemin absolu pour le chemin local donné.

    Args:
        local_path (str): Le chemin local à convertir en chemin absolu.

    Returns:
        str: Le chemin absolu correspondant.
    """
    return os.path.abspath(local_path)


def find_window_by_type(type, get_frame=False):
    """
    Recherche et retourne une fenêtre et son index par son type dans la liste des fenêtres.

    Args:
        type (str): Le type de fenêtre à rechercher.
        get_frame (bool, optional): Si True, retourne le cadre associé à la fenêtre (par défaut: False).

    Returns:
        tuple: Un tuple contenant la fenêtre et son index dans la liste des fenêtres, ou (None, 0) si non trouvé.
    """
    index = 0
    global list_of_windows
    #obj_window = {"type": "main", "window": tk, "frame": tk.frame}
    for obj_window in list_of_windows:
        if(type == obj_window["type"]):
            if(get_frame):
                if 'frame' in obj_window:
                    return obj_window["frame"]
            return obj_window["window"], index
        index += 1
    
    return None, 0


def add_window(type, window, replace=True, frame=None):
    """
    Ajoute une fenêtre à la liste des fenêtres. Si replace est True, remplace la fenêtre existante du même type.

    Args:
        type (str): Le type de fenêtre à ajouter.
        window (tk.Toplevel): La fenêtre à ajouter.
        replace (bool, optional): Si True, remplace la fenêtre existante du même type (par défaut: True).
        frame (tk.Frame, optional): Le cadre associé à la fenêtre (par défaut: None).

    Returns:
        None
    """
    existing_window, window_index = find_window_by_type(type)
    window_already_exist = True
    if(existing_window == None): window_already_exist = False

    if(replace and window_already_exist):
        existing_window.destroy()
        list_of_windows[window_index] = {"type": type, "window": window}

        if(frame != None):
            list_of_windows[window_index]["frame"] = frame

        return
    
    list_of_windows.append({"type": type, "window": window})
    if(frame != None):
            list_of_windows[window_index]["frame"] = frame

    return


def close_window_and_remove_from_list(window_type):
    """
    Ferme la fenêtre du type spécifié et la supprime de la liste des fenêtres.

    Args:
        window_type (str): Le type de fenêtre à fermer.

    Returns:
        None
    """
    window, ind = find_window_by_type(window_type)
    if window and ind is not None:
        list_of_windows.pop(ind)
        window.destroy()


def check_history_file(folder_path):
    """
    Vérifie si des dossiers sont manquants en comparant le fichier history.json aux dossiers présents.

    Args:
        folder_path (str): Le chemin du dossier contenant le fichier history.json.

    Returns:
        list: Une liste des dossiers manquants.
    """"""
    Vérifie si des dossiers sont manquants en comparant le fichier history.json aux dossiers présents.

    :param folder_path: str, le chemin du dossier contenant le fichier history.json
    :return: list, une liste des dossiers manquants
    """
    missing_folders = []

    # MODIFICATION TO GET THE HISTORY FILE HERE
    with open(os.path.join(folder_path, "history.json"), "r") as file:
        history_data = json.load(file)

    for entry in history_data:
        setup_name = entry['setupName']
        setup_folder_path = os.path.join(folder_path, setup_name)

        if not os.path.exists(setup_folder_path):
            missing_folders.append(setup_name)

    return missing_folders


# Function to get the server files path from the options.txt file
def get_server_files_path():
    """
    Récupère le chemin des fichiers du serveur à partir du fichier options.txt.

    Returns:
        str: Le chemin absolu des fichiers du serveur.
    """
    # MODIFICATION TO LIST PATIENTS FOLDERS HERE

    with open("options.txt", "r") as file:
        for line in file.readlines():
            if line.startswith("SERVER_FILES_PATH="):
                return get_absolute_path(line.strip().split("=")[1])
    return None

# Function to open the folder in the file explorer
def open_folder(folder_path):
    """
    Ouvre le dossier spécifié dans l'explorateur de fichiers.

    Args:
        folder_path (str): Le chemin du dossier à ouvrir.

    Returns:
        None
    """
    os.startfile(os.path.abspath(folder_path))


def update_main_window(window, frame, server_files_path):
    """
    Met à jour la fenêtre principale en reconstruisant les boutons de dossier en fonction des dossiers présents dans le chemin des fichiers du serveur.

    Args:
        window (tk.Tk): La fenêtre principale.
        frame (tk.Frame): Le cadre contenant les boutons de dossier.
        server_files_path (str): Le chemin d'accès au dossier contenant les fichiers du serveur.

    Returns:
        None
    """
    for child in frame.winfo_children():
        child.destroy()

    folder_list = [folder for folder in os.listdir(server_files_path) if os.path.isdir(os.path.join(server_files_path, folder))]
    server_files_path.replace('\\\\', '\\')
    create_buttons_for_folders(window, frame, folder_list, server_files_path)  # Mettez à jour la liste des boutons


def create_new_patient_window(parent, server_files_path, frame):
    """
    Crée et affiche une fenêtre "Nouveau patient" pour saisir les informations d'un nouveau patient et créer un nouveau dossier patient dans les fichiers du serveur.

    Args:
        parent (tk.Widget): La fenêtre parente à laquelle la fenêtre "Nouveau patient" sera attachée.
        server_files_path (str): Le chemin d'accès au dossier contenant les fichiers du serveur.
        frame (tk.Frame): Le cadre contenant les boutons de dossier dans la fenêtre parente.

    Returns:
        None
    """
    type = "new_patient_window"
    if(find_window_by_type(type) == (None, 0)):
        new_patient_window = tk.Toplevel(parent)
        new_patient_window.title("Aligneurs français - New Patient")
        new_patient_window.iconbitmap('AF.ico')
        new_patient_window.configure(bg='#2b2b2b')

        add_window(type=type, window=new_patient_window)

        patient_label = tk.Label(new_patient_window, text="Nom du dossier patient", bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        patient_label.pack(pady=10)
        practicien_label_ex = tk.Label(new_patient_window, text="ex: jean_lefebvre", bg='#2b2b2b', fg='white', font=('Arial', 8))
        practicien_label_ex.pack(pady=0)

        patient_entry = tk.Entry(new_patient_window, font=('Arial', 10))
        patient_entry.pack(pady=5)

        # practicien_label = tk.Label(new_patient_window, text="Nom du praticien", bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        # practicien_label.pack(pady=10)

        # practicien_label_ex = tk.Label(new_patient_window, text="ex: Marcel Lambert", bg='#2b2b2b', fg='white', font=('Arial', 8))
        # practicien_label_ex.pack(pady=0)

        # practicien_entry = tk.Entry(new_patient_window, font=('Arial', 10))
        # practicien_entry.pack(pady=5)

        warning_label = tk.Label(new_patient_window, text="", bg='#2b2b2b', fg='red', font=('Arial', 8))
        warning_label.pack(pady=10)

        # Nouvelle fonction pour gérer le clic sur le bouton "Créer"
        def create_button_click(event):
            """
            Gère le clic sur le bouton "Créer" dans la fenêtre "Nouveau patient" et crée un nouveau dossier patient.
            Met à jour la fenêtre principale si la création a réussi.

            Args:
                event (tk.Event): L'événement de clic.

            Returns:
                None
            """
            # result = create_new_patient_folder(server_files_path, patient_entry.get(), practicien_entry.get())
            result = create_new_patient_folder(server_files_path, patient_entry.get())
            if (result == True):
                new_patient_window.destroy()
                update_main_window(parent, frame, server_files_path)  # Mettez à jour la liste des boutonsupdate_main_window(parent, frame, server_files_path)
                window, ind = find_window_by_type(type)
                list_of_windows.pop(ind)
            else:
                warning_label.config(text=result)

        create_button = create_styled_button(new_patient_window, text="Créer", width=100, height=30, button_color="00ff00")
        create_button.bind('<Button-1>', lambda event: create_button_click(event))
        create_button.pack(pady=10)

        # Set the maximum width for the window
        new_patient_window.update_idletasks()
        content_height = new_patient_window.winfo_reqheight()
        content_width = new_patient_window.winfo_reqwidth()
        new_patient_window.geometry(str(content_width+30)+"x"+str(content_height+20))

        new_patient_window.protocol("WM_DELETE_WINDOW", lambda: close_window_and_remove_from_list(type))



def create_new_patient_folder(server_files_path, patient_name, practicien_entry=""):
    """
    Crée un nouveau dossier patient dans le dossier des fichiers du serveur avec le nom du patient donné.

    Args:
        server_files_path (str): Le chemin d'accès au dossier contenant les fichiers du serveur.
        patient_name (str): Le nom du patient pour le nouveau dossier patient.
        practicien_entry (str): Le nom du praticien pour le nouveau dossier patient. [DEPRECATED]

    Returns:
        Union[bool, str]: True si la création a réussi, sinon un message d'erreur indiquant la raison de l'échec.
    """
    if (not patient_name):
        return "Veuillez saisir le nom du dossier patient"
    # if(len(practicien_entry.split(' ')) != 2):
    #     return "Le nom du praticien doit être composé de deux mots"

    new_patient_folder = os.path.join(server_files_path, patient_name)

    if os.path.isdir(new_patient_folder):
        return "Ce dossier patient existe déjà"
    # MODIFICATION TO GENERATE THE PATIENT FOLDER HERE
    os.makedirs(new_patient_folder, exist_ok=True)

    # MODIFICATION TO POST THE HISTORY FILE HERE
    history_file_path = os.path.join(new_patient_folder, "history.json")
    history_data = [
        {
            "eventName": "Setup 1",
            "setupName": "Setup_1",
            "visible": True,
            "date": datetime.today().strftime('%d/%m/%Y'),
            "timestamp": "Actuel",
            "status": "En attente",
            "chatHistory": []
        }
    ]

    with open(history_file_path, 'w', encoding='utf-8') as history_file:
        json.dump(history_data, history_file, indent=4, ensure_ascii=False)

    return True
                # {
                    # "id": round(random() * 4),
                    # "title": "Dr.",
                    # "firstName": practicien_entry.split(' ')[0],
                    # "lastName": practicien_entry.split(' ')[1],
                    # "msg": "",
                    # "modifications": []
                # }


def filter_folders(search_text, folder_data):
    """
    Filtre les dossiers en fonction du texte de recherche.

    Args:
        search_text (str): Le texte à rechercher.
        folder_data (list): La liste des noms de dossier.

    Returns:
        list: Une liste des dossiers filtrés.
    """
    search_text_normalized = unidecode.unidecode(search_text.lower().strip())

    if not search_text_normalized:
        return folder_data

    filtered_data = []
    for data in folder_data:
        folder_name = unidecode.unidecode(data.lower()) 
        if search_text_normalized in folder_name:
            filtered_data.append(data)

    return filtered_data


def on_search_text_changed(search_text, frame, server_files_path):
    """
    Appelé lorsque le texte de recherche change.

    Args:
        search_text (tk.StringVar): Le texte de recherche.
        frame (tk.Frame): Le cadre contenant les boutons de dossier.
        server_files_path (str): Le chemin des fichiers du serveur.

    Returns:
        None
    """
    display_filtered_buttons(search_text.get(), frame, server_files_path)



def display_filtered_buttons(search_text, frame, server_files_path):
    """
    Affiche les boutons de dossier filtrés en fonction du texte de recherche.

    Args:
        search_text (str): Le texte de recherche.
        frame (tk.Frame): Le cadre contenant les boutons de dossier.
        server_files_path (str): Le chemin des fichiers du serveur.

    Returns:
        None
    """
    button_list = []
    folder_data = []
    
    # Supprimez les boutons existants
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            button_list.append(widget)
            folder_data.append(widget.cget("text"))
            widget.grid_forget()

    filtered_data = filter_folders(search_text, folder_data)

    # Affichez les boutons filtrés
    buttons_per_row = 4
    padx = 10
    pady = 10

    index = 0

    for button in button_list:
        if button.cget("text") in filtered_data:  # Vérifiez si le texte du bouton est présent dans folder_data
            row = index // buttons_per_row
            column = index % buttons_per_row
            button.grid(row=row, column=column, padx=padx, pady=pady)
            index += 1  # Mettez à jour l'index seulement si le bouton a été affiché


def create_interface(folder_list, server_files_path):
    """
    Crée l'interface principale avec les boutons de dossier.

    Args:
        folder_list (list): La liste des noms de dossier.
        server_files_path (str): Le chemin des fichiers du serveur.

    Returns:
        None
    """
    window = tk.Tk()
    window.title("Interface")
    window.configure(bg='#2b2b2b')
    window.iconbitmap('AF.ico')

    canvas = tk.Canvas(window, width=640, height=200, bg='#2b2b2b', highlightthickness=0)
    canvas.pack(side='left', fill='both', expand=True)

    scrollbar = tk.Scrollbar(window, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    search_and_new_patient_frame = tk.Frame(window, bg='#2b2b2b')
    search_and_new_patient_frame.pack(side='top', fill='x', padx=10, pady=5)

    search_text = tk.StringVar()
    search_entry = tk.Entry(search_and_new_patient_frame, textvariable=search_text, width=20)
    search_entry.grid(row=0, column=0, padx=5, pady=5)

    def on_entry_click(event):
        if search_entry.get() == 'Rechercher...':
            search_entry.delete(0, "end")
            search_entry.config(fg='black')

    def on_entry_focus_out(event):
        if search_entry.get() == '':
            search_entry.insert(0, 'Rechercher...')
            search_entry.config(fg='grey')

    search_entry.insert(0, 'Rechercher...')
    search_entry.config(fg='grey')
    search_entry.bind('<FocusIn>', on_entry_click)
    search_entry.bind('<FocusOut>', on_entry_focus_out)

    on_search_text_changed_wrapper = lambda *args: on_search_text_changed(search_text, frame, server_files_path)
    search_text.trace('w', on_search_text_changed_wrapper)

    # Bind the mouse wheel event for scrolling
    # def scroll_canvas(event):
    #     canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    #     check_scroll_position(canvas)

    # window.bind("<MouseWheel>", scroll_canvas)

    frame = tk.Frame(canvas, bg='#2b2b2b')
    canvas.create_window((0, 0), window=frame, anchor='nw')

    create_buttons_for_folders(window, frame, folder_list, server_files_path)

    new_patient_button = create_styled_button(search_and_new_patient_frame, text="Nouveau patient", width=150, height=30, button_color="ff0000")
    new_patient_button.bind('<Button-1>', lambda event: create_new_patient_window(window, server_files_path, frame))
    new_patient_button.grid(row=1, column=0, padx=5, pady=5, sticky='S')

    add_window(type="main", window=window, frame=frame)
    # Set the maximum width for the window
    window.update_idletasks()
    content_height = window.winfo_reqheight()
    content_width = window.winfo_reqwidth()
    window.geometry(str(content_width+60)+"x"+str(content_height))
    window.mainloop()


def create_buttons_for_folders(window, frame, folder_list, server_files_path):
    """
    Crée et affiche des boutons pour chaque dossier dans la liste des dossiers donnée.

    Args:
        window (tk.Tk): La fenêtre principale.
        frame (tk.Frame): Le cadre contenant les boutons de dossier.
        folder_list (List[str]): La liste des noms de dossier pour lesquels créer des boutons.
        server_files_path (str): Le chemin d'accès au dossier contenant les fichiers du serveur.

    Returns:
        None
    """
    buttons_per_row = 4
    button_width = 150
    button_height = 50
    radius = 15
    padx = 10
    pady = 10

    folder_data = []

    for folder in folder_list:
        missing_folders = check_history_file(os.path.join(server_files_path, folder))
        with open(os.path.join(server_files_path, folder, "history.json"), "r") as file:
            history_data = json.load(file)
            date = history_data[0]["date"]

        folder_data.append({"folder": folder, "missing_folders": missing_folders, "date": date})

    folder_data.sort(key=lambda x: (len(x["missing_folders"]) == 0, x["date"]), reverse=False)

    
    for index, folder_dict in enumerate(folder_data):
        folder = folder_dict["folder"]
        missing_folders = folder_dict["missing_folders"]

        row = index // buttons_per_row
        column = index % buttons_per_row

        if missing_folders:
            button_image_normal = create_rounded_rect_with_circle(button_width, button_height, radius, "#4d4d4d", small_circle=True)
            button_image_active = create_rounded_rect_with_circle(button_width, button_height, radius, "#3b3b3b", small_circle=True)
        else:
            button_image_normal = create_rounded_rect(button_width, button_height, radius, "#4d4d4d")
            button_image_active = create_rounded_rect(button_width, button_height, radius, "#3b3b3b")

        button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)
        button_image_active_tk = ImageTk.PhotoImage(button_image_active)

        folder_button = tk.Button(frame, text=folder, width=button_width, height=button_height, font=('Arial', 10, 'bold'), fg='white', image=button_image_normal_tk, compound=tk.CENTER, relief=tk.FLAT, padx=0, pady=0, bg='#2b2b2b', activebackground='#2b2b2b', bd=0)

        folder_button.image_normal = button_image_normal_tk
        folder_button.image_active = button_image_active_tk

        folder_button.bind('<Enter>', lambda event, button=folder_button: button.config(image=button.image_active))
        folder_button.bind('<Leave>', lambda event, button=folder_button: button.config(image=button.image_normal))

        folder_button.bind('<Button-1>', lambda event, f=folder: display_folder_details(window, os.path.join(server_files_path, f), os.path.join(server_files_path, f, 'history.json')))
        folder_button.grid(row=row, column=column, padx=padx, pady=pady)



def check_scroll_position(canvas):
    """
    Vérifie la position de défilement du canevas et ajuste la position de défilement si nécessaire.

    Args:
        canvas (tk.Canvas): Le canevas dont la position de défilement doit être vérifiée.

    Returns:
        None
    """
    x1, y1, x2, y2 = canvas.bbox("all")
    if y1 < 0:
        canvas.yview_scroll(-1 * y1, "units")


def display_folder_details(parent, folder_path, history_file_path, labelBgColor="#808080", max_width=550):
    """
    Affiche les détails du dossier dans une nouvelle fenêtre.

    Args:
        parent (tk.Tk): La fenêtre parente.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        labelBgColor (str, optional): La couleur d'arrière-plan des étiquettes. Par défaut "#808080".
        max_width (int, optional): La largeur maximale de la fenêtre. Par défaut 550.
    
    Returns:
        None
    """
    detail_window = create_detail_window(parent, folder_path)
    display_detail_window_content(parent, detail_window, folder_path, history_file_path, labelBgColor=labelBgColor, max_width=550)


def create_detail_window(parent, folder_path):
    """
    Crée une nouvelle fenêtre de détails pour le dossier spécifié.

    Args:
        parent (tk.Tk): La fenêtre parente.
        folder_path (str): Le chemin d'accès au dossier.

    Returns:
        tk.Toplevel: La nouvelle fenêtre de détails créée, ou None si une fenêtre du même type existe déjà.
    """
    type = "folder_detail_" + os.path.basename(folder_path)

    if find_window_by_type(type) == (None, 0):
        detail_window = tk.Toplevel(parent)
        detail_window.title(f"{parent.title()} - {os.path.basename(folder_path)}")
        detail_window.iconbitmap('AF.ico')
        detail_window.configure(bg='#2b2b2b')

        add_window(type=type, window=detail_window)

        detail_window.columnconfigure(0, weight=1)
        detail_window.rowconfigure(0, weight=1)

        detail_window.protocol("WM_DELETE_WINDOW", lambda: close_window_and_remove_from_list(type))

        return detail_window
    else:
        return None
    

def open_reply_window(parent, detail_window, folder_path, index, history_data, history_file_path, title, bg, type):
    """
    Ouvre une nouvelle fenêtre de réponse pour permettre à l'utilisateur de rédiger et d'envoyer une réponse.

    Args:
        parent (tk.Tk): La fenêtre parente.
        detail_window (tk.Toplevel): La fenêtre de détail.
        folder_path (str): Le chemin d'accès au dossier.
        index (int): L'index de l'élément d'historique.
        history_data (list): Les données d'historique.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        title (str): Le titre de la fenêtre de réponse.
        bg (str): La couleur d'arrière-plan de la fenêtre de réponse.
        type (str): Le type de fenêtre.
    
    Returns:
        None
    """
    if(find_window_by_type(type) == (None, 0)):
        reply_window = tk.Toplevel()
        reply_window.iconbitmap('AF.ico')
        reply_window.title(title)
        reply_window.configure(bg=bg)

        # reply_text = tk.StringVar()

        reply_entry = tk.Text(reply_window, wrap=tk.WORD, height=4, width=50, font=("Arial", 10))

        # reply_entry = create_styled_entry(reply_window, width=50, height=30, textvariable=reply_text, entry_color="ffffff", text_color="ffffff")
        reply_entry.pack(padx=10, pady=10)

        send_button = create_styled_button(reply_window, text="Envoyer", width=150, height=30, button_color="0000ff")
        send_button.bind('<Button-1>', lambda event: save_reply_and_close_window(index, history_data, history_file_path, reply_entry.get("1.0", tk.END).strip(), type, parent, detail_window, folder_path))
        send_button.pack(padx=10, pady=10)

        add_window(type=type, window=reply_window)
        reply_window.protocol("WM_DELETE_WINDOW", lambda: close_window_and_remove_from_list(type))


def save_reply_and_close_window(index, history_data, history_file_path, reply_message, type, parent, detail_window, folder_path):
    """
    Enregistre la réponse, met à jour le fichier d'historique JSON, rafraîchit la fenêtre de détails et ferme la fenêtre de réponse.

    Args:
        index (int): L'index de l'élément d'historique.
        history_data (list): Les données d'historique.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        reply_message (str): Le message de réponse.
        type (str): Le type de fenêtre.
        parent (tk.Tk): La fenêtre parente.
        detail_window (tk.Toplevel): La fenais): La fenêtre de détail.
        folder_path (str): Le chemin d'accès au dossier.
    
    Returns:
        None
    """
    # MODIFICATION TO POST ON THE HISTORY FILE HERE
    new_reply = {
        "id": round(random() * 10000),
        "date": datetime.today().strftime('%d/%m/%Y'),
        "title": "Aligneurs",
        "firstName": "Francais",
        "lastName": "Comments",
        "msg": reply_message,
        "modifications": []
    }

    history_data[index]["chatHistory"].append(new_reply)

    with open(history_file_path, 'w', encoding='utf-8') as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)

    # Refresh detail_window content
    refresh_detail_window_content(parent, detail_window, folder_path, history_file_path)

    # reply_window.destroy()
    close_window_and_remove_from_list(type)


def display_detail_window_content(parent, detail_window, folder_path, history_file_path, labelBgColor="#808080", max_width=550):
    """
    Affiche le contenu de la fenêtre de détails en lisant le fichier d'historique JSON et en créant les widgets appropriés.
    Args:
        parent (tk.Tk): La fenêtre parente.
        detail_window (tk.Toplevel): La fenêtre de détail.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        labelBgColor (str, optional): La couleur d'arrière-plan des étiquettes. Par défaut "#808080".
        max_width (int, optional): La largeur maximale de la fenêtre. Par défaut 550.
    
    Returns:
        None
    """
    if detail_window is None:
        return
    
    # Read history.json file
    # MODIFICATION TO GET THE HISTORY FILE HERE
    with open(history_file_path, 'r', encoding='utf-8') as file:
        history_data = json.load(file)

    # Create a container frame to hold canvas and scrollbar
    container_frame = tk.Frame(detail_window)
    container_frame.pack(side='left', fill='both', expand=True, padx=5)

    canvas = tk.Canvas(container_frame, bg='#2b2b2b')
    canvas.pack(side='left', fill='both', expand=True)

    scrollbar = tk.Scrollbar(detail_window, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    # Bind the mouse wheel event for scrolling
    def scroll_canvas(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        check_scroll_position(canvas)

    detail_window.bind("<MouseWheel>", scroll_canvas)

    detail_frame = tk.Frame(canvas, bg='#2b2b2b', padx=10, pady=0)
    canvas.create_window((0, 0), window=detail_frame, anchor='nw')

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    detail_frame.bind('<Configure>', update_scrollregion)

    label_width = 40
    dark_bg_color = darker_color(labelBgColor)

    index = 0
    for data in history_data:
        button_color = "0000ff"
        if not os.path.exists(os.path.join(folder_path, data["setupName"])):
            button_color = "ff0000"

        status_button = create_styled_button(detail_frame, text=data["eventName"], width=150, height=50, button_color=button_color)
        if button_color == "ff0000":
            status_button.bind('<Button-1>', lambda event, f=data["setupName"]: display_uncompression_windows(parent, os.path.join(folder_path, f), history_file_path))

        status_button.grid(row=index, column=0, padx=5, pady=5, sticky='ne')

        label_frame = tk.Frame(detail_frame, bg=dark_bg_color)
        label_frame.grid(row=index, column=1, sticky='w')

        reply_button = tk.Button(label_frame, text="Répondre", command=lambda index=index : open_reply_window(parent, detail_window, folder_path, index, history_data, history_file_path, detail_window.title() + " - " + history_data[index]["eventName"], detail_window["bg"], "response_window_"+os.path.basename(folder_path)+"_"+history_data[index]["setupName"]))
        reply_button.pack(side='bottom', anchor='e', padx=5, pady=5)


        if(len(data["chatHistory"]) == 0):
            header_label = tk.Label(label_frame, text="Aucun détail disponible", bg=labelBgColor, fg='white', font=('Arial', 10, 'bold', 'underline'), padx=10, pady=5, width=label_width, anchor='w')
            header_label.pack(side='top')

        for index2, event in enumerate(data["chatHistory"]):
            date = data['date']
            if('date' in event): date = event['date']

            event_header = f"{date} - {event['title']} {event['firstName']} {event['lastName']}"

            header_label = tk.Label(label_frame, text=event_header, bg=labelBgColor, fg='white', font=('Arial', 10, 'bold', 'underline'), padx=10, pady=5, width=label_width, anchor='w')
            header_label.pack(side='top')

            message_label = tk.Label(label_frame, text=event['msg'], bg=labelBgColor, fg='white', font=('Arial', 10, 'italic'), padx=10, pady=5, width=label_width, anchor='w')
            message_label.pack(side='top')

            if event["modifications"]:
                for mod in event["modifications"]:
                    mod_label_text = f"{mod['tooth']}:".replace("-", "\n")
                    if mod['tooth'][0:6] != "Global":
                        mod_label_text = "Dent " + mod_label_text

                    tooth_modifications = "\n".join([f"{tooth_mod['type']} : {tooth_mod['value']}" for tooth_mod in mod["modifications"]])

                    mod_frame = tk.Frame(label_frame, bg=dark_bg_color, width=label_width)
                    mod_frame.pack(side='top', anchor='w', pady=5)

                    tooth_label = tk.Label(mod_frame, text=mod_label_text, bg=labelBgColor, fg='white', font=('Arial', 10), padx=10, pady=5, bd=1, width=round(label_width/3))
                    tooth_label.grid(row=0, column=0, sticky='nw')

                    modifications_label = tk.Label(mod_frame, text=tooth_modifications, bg=labelBgColor, fg='white', font=('Arial', 10), padx=10, pady=5, relief='groove', bd=1)
                    modifications_label.grid(row=1, column=1, sticky='ne')
        index += 1

    # Créer un nouveau cadre pour contenir le bouton et le cadre container_frame
    main_frame = tk.Frame(detail_window, bg='#2b2b2b')
    main_frame.pack(side='top', fill='both', expand=True, pady=5)

    # Ajouter un bouton pour ajouter un nouveau setup
    add_setup_button = create_styled_button(main_frame, text="Ajouter Setup", width=120, height=40, button_color="008000")
    add_setup_button.pack(side='top', padx=5)
    add_setup_button.bind('<Button-1>', lambda event: add_new_setup_and_refresh(detail_window, folder_path, history_file_path, labelBgColor, max_width))

    # Set the maximum width for the window
    detail_window.update_idletasks()
    detail_frame_height = detail_frame.winfo_reqheight()
    detail_frame_width = detail_frame.winfo_reqwidth()
    main_frame_height = main_frame.winfo_reqheight()
    main_frame_width = main_frame.winfo_reqwidth()
    content_width = detail_frame_width + main_frame_width
    content_height = detail_frame_height
    
    detail_window.maxsize(width=content_width+20, height=content_height)
    detail_window.geometry(str(content_width+20)+"x"+str(content_height))

        
def add_new_setup_to_history(history_file_path):
    with open(history_file_path, 'r', encoding='utf-8') as file:
        history_data = json.load(file)

    # Création d'une liste contenant tous les "eventName"
    event_names = [data["eventName"] for data in history_data]

    # Trouver le chiffre le plus grand dans les "eventName"
    last_setup_number = find_largest_number(event_names)
    new_setup_number = last_setup_number + 1

    new_setup = {
        "eventName": f"Setup {new_setup_number}",
        "setupName": f"Setup_{new_setup_number}",
        "visible": True,
        "date": datetime.today().strftime('%d/%m/%Y'),
        "timestamp": "Actuel",
        "status": "En attente",
        "chatHistory": []
    }
    history_data.insert(0, new_setup)
    # MODIFICATION TO POST THE HISTORY FILE HERE
    with open(history_file_path, 'w', encoding='utf-8') as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)



def find_largest_number(strings_list):
    largest_number = 0
    for s in strings_list:
        numbers = [int(num) for num in s.split() if num.isdigit()]
        largest_number = max(largest_number, *numbers)
    return largest_number


def add_new_setup_and_refresh(detail_window, folder_path, history_file_path, labelBgColor, max_width):
    add_new_setup_to_history(history_file_path)
    refresh_detail_window_content(detail_window.master, detail_window, folder_path, history_file_path, labelBgColor, max_width)


def refresh_detail_window_content(parent, detail_window, folder_path, history_file_path, labelBgColor="#808080", max_width=550):
    """
    Rafraîchit le contenu de la fenêtre de détails en supprimant le contenu existant et en affichant le contenu mis à jour.

    Args:
        parent (tk.Tk): La fenêtre parente.
        detail_window (tk.Toplevel): La fenêtre de détail.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        labelBgColor (str, optional): La couleur d'arrière-plan des étiquettes. Par défaut "#808080".
        max_width (int, optional): La largeur maximale de la fenêtre. Par défaut 550.

    Returns:
        None
    """
    if(detail_window is None): return
    # Remove existing content
    for widget in detail_window.winfo_children():
        widget.destroy()

    # Display updated content
    display_detail_window_content(parent, detail_window, folder_path, history_file_path, labelBgColor, max_width)


def get_global_variable(name):
    """
    Récupère la valeur d'une variable globale dans le fichier options.txt.

    Args:
        name (str): Le nom de la variable globale à rechercher.

    Returns:
        str: La valeur de la variable globale, ou None si la variable n'est pas trouvée.
    """
    with open("options.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(name+"="):
                return get_absolute_path(line.strip().split("=")[1])

    return None


def open_obj_opt_window(root, folder_path, history_file_path):
    """
    Ouvre la fenêtre d'optimisation d'objet et lance le processus d'optimisation.

    Args:
        root (tk.Tk): La fenêtre racine de l'application.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.

    Returns:
        None
    """
    type = "adding_setup_"+ find_patient_name_from_path(folder_path) + "_" +os.path.basename(folder_path)

    if(find_window_by_type(type) == (None, 0)):

        obj_opt_window = tk.Toplevel(root)
        obj_opt_window.title(f"{root.title()}")
        obj_opt_window.iconbitmap('AF.ico')
        obj_opt_window.configure(bg='#2b2b2b')
        max_width= 500

        add_window(type=type, window=obj_opt_window)

        status_label_var = tk.StringVar()
        status_label_var.set("En cours...")

        output_label_var = tk.StringVar()
        output_label_var.set("Chargement")

        status_label = tk.Label(obj_opt_window, textvariable=status_label_var, bg="dark gray")
        status_label.pack(pady=10)

        # output_label = create_styled_label(obj_opt_window, text=output_label_var, width=500, height=200)
        output_label = tk.Label(obj_opt_window, textvariable=output_label_var, fg='white', bg='#2b2b2b')
        output_label.pack(pady=10)

        obj_opt_thread = Thread(target=run_obj_optimization, args=(status_label_var, output_label_var, status_label, obj_opt_window, folder_path, history_file_path), daemon=True)
        obj_opt_thread.start()

        # Set the maximum width for the window
        obj_opt_window.update_idletasks()
        content_height = obj_opt_window.winfo_reqheight()
        # obj_opt_window.maxsize(width=max_width, height=content_height)
        obj_opt_window.geometry(str(max_width)+"x"+str(content_height))

        obj_opt_window.protocol("WM_DELETE_WINDOW", lambda: close_window_and_remove_from_list(type))


def read_process_output(process, output_label_var, obj_opt_window):
    """
    Lit la sortie d'un processus en cours d'exécution et met à jour la fenêtre d'optimisation d'objet avec les deux dernières lignes de la sortie.

    Args:
        process (subprocess.Popen): Le processus en cours d'exécution.
        output_label_var (tk.StringVar): La variable pour stocker la sortie du processus.
        obj_opt_window (tk.Toplevel): La fenêtre d'optimisation d'objet.

    Returns:
        None
    """

    last_two_lines = ["", ""]
    
    for line in process.stdout:
        last_two_lines.pop(0)
        last_two_lines.append(line.strip())
        output_label_var.set("\n".join(last_two_lines))
        obj_opt_window.update_idletasks()
        content_height = obj_opt_window.winfo_reqheight()
        obj_opt_window.geometry(str(500)+"x"+str(content_height))
    process.communicate()


def find_patient_name_from_path(path):
    """
    Trouve le nom du patient à partir du chemin d'accès.

    Args:
        path (str): Le chemin d'accès.

    Returns:
        str: Le nom du patient, ou None si le nom n'est pas trouvé.
    """

    path = path.replace('\\', '/')
    pattern = r'/([^/]+)/[^/]+$'
    match = re.search(pattern, path)
    if match:
        return match.group(1)
    return None


def find_last_part_from_path(path):
    """
    Trouve la dernière partie du chemin d'accès.

    Args:
        path (str): Le chemin d'accès.

    Returns:
        str: La dernière partie du chemin d'accès.
    """
    path = path.replace('\\', '/')
    parts = path.split('/')
    return parts[-1]


def recreate_directory(path, only_create=True):
    if os.path.exists(path) and not only_create:
        shutil.rmtree(path)
    if not os.path.exists(path): os.mkdir(path)


def destroy_path(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def run_obj_optimization(status_label_var, output_label_var, status_label, obj_opt_window, folder_path, history_file_path):
    """
    Exécute l'optimisation d'objet en utilisant un script d'optimisation externe et met à jour l'interface utilisateur en fonction des résultats.

    Args:
        status_label_var (tk.StringVar): La variable pour stocker le statut de l'optimisation.
        output_label_var (tk.StringVar): La variable pour stocker la sortie du processus d'optimisation.
        status_label (tk.Label): L'étiquette pour afficher le statut de l'optimisation.
        obj_opt_window (tkToplevel): La fenêtre d'optimisation d'objet.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.

    Returns:
        None
    """
    obj_opt_file = get_global_variable("PYTHON_OPTIMIZING_FILE")
    extract_path = get_global_variable("EXTRACT_FILES_TO")
    global optimization_is_launched

    extract_path = get_global_variable("EXTRACT_FILES_TO")
    splitted_path = get_global_variable("SPLITTED_DATA_DIR")
    optimized_path = get_global_variable("OPTIMIZED_DATA_DIR")
    export_path = get_global_variable("EXPORT_DATA_DIR")
    abs_extract_path = os.path.abspath(extract_path)
    abs_splitted_path = os.path.abspath(splitted_path)
    abs_optimized_path = os.path.abspath(optimized_path)
    abs_export_path = os.path.abspath(export_path)
    setup_name = folder_path.split('\\')[-1]
    patientName = folder_path.split('\\')[-2]
    # recreate_directory(os.path.join(abs_extract_path, patientName))
    # recreate_directory(os.path.join(abs_extract_path, patientName, setup_name))
    recreate_directory(os.path.join(abs_splitted_path, patientName))
    recreate_directory(os.path.join(abs_splitted_path, patientName, setup_name))
    recreate_directory(os.path.join(abs_optimized_path, patientName))
    recreate_directory(os.path.join(abs_optimized_path, patientName, setup_name))
    recreate_directory(os.path.join(abs_export_path, patientName))
    recreate_directory(os.path.join(abs_export_path, patientName, setup_name))


    if obj_opt_file is None:
        status_label_var.set("Erreur")
        status_label.config(bg="red")
        output_label_var.set("Le chemin du script d'optimisation d'objet n'a pas été trouvé dans le fichier options.txt")
        print("Le chemin du script d'optimisation d'objet n'a pas été trouvé dans le fichier options.txt")
        return

    # Vérification de la présence des fichiers requis
    required_files = ["landmarks.txt", "IPR.csv", "Movement table.csv"]
    missing_files = []

    for file in required_files:
        if not os.path.isfile(os.path.join(os.path.join(abs_extract_path, patientName, setup_name), file)):
            missing_files.append(file)

    if missing_files:
        status_label_var.set("Erreur")
        status_label.config(bg="red")
        output_label_var.set("Fichiers manquants : " + ", ".join(missing_files))
        return
    
    # Vérification que la procédure d'optimisation est libre
    if(optimization_is_launched):
        status_label_var.set("Erreur")
        status_label.config(bg="red")
        output_label_var.set("Une séquence d'optimisation a déjà été lancée\n Veuillez attendre que celle-ci soit terminée")
        return
    
    
    # optimization_is_launched = True
    options_file_path = os.path.abspath("options.txt")
    obj_opt_path = os.path.abspath(os.path.join(os.path.dirname(options_file_path), obj_opt_file))
    obj_opt_dir = os.path.dirname(os.path.abspath(obj_opt_path))

    # Create paths
    extract_full_path = os.path.join(abs_extract_path, patientName, setup_name)
    splitted_full_path = os.path.join(abs_splitted_path, patientName, setup_name)
    optimized_full_path = os.path.join(abs_optimized_path, patientName, setup_name)
    export_full_path = os.path.join(abs_export_path, patientName, setup_name)

    # Add paths as arguments
    process = subprocess.Popen(["python", "-u", obj_opt_path, extract_full_path, splitted_full_path, optimized_full_path, export_full_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=obj_opt_dir)
   
    # Création d'un thread pour lire la sortie du processus
    read_output_thread = threading.Thread(target=read_process_output, args=(process, output_label_var, obj_opt_window))
    read_output_thread.start()

    read_output_thread.join()

    # ___________ SUCCESS __________
    if process.returncode == 0:
        # Créer le dossier de destination
        dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_path)
        # MODIFICATION TO CREATE THE SETUP FOLDER HERE
        os.makedirs(dest_dir, exist_ok=True)

        # Trouver le chemin du dossier optimisé
        optimized_data_dir = get_global_variable("OPTIMIZED_DATA_DIR")
        if optimized_data_dir is None:
            print("Le chemin du dossier optimisé n'a pas été trouvé dans le fichier options.txt")
            return

        optimized_data_path = os.path.abspath(os.path.join(os.path.dirname(options_file_path), optimized_data_dir))

        # Copier les fichiers et dossiers du dossier optimisé vers le dossier de destination
        for item in os.listdir(export_full_path):
            src_item_path = os.path.join(export_full_path, item)
            dest_item_path = os.path.join(dest_dir, item)
            # MODIFICATION TO POST ALL OF THE FILES GENERATED HERE
            if os.path.isdir(src_item_path):
                shutil.copytree(src_item_path, dest_item_path)
            else:
                shutil.copy2(src_item_path, dest_item_path)
        
        # On récupère la fenêtre principale
        main_window, ind = find_window_by_type("main")
        main_frame = find_window_by_type("main", get_frame=True)
        # On récupère la fenêtre a rafraichir
        type = "folder_detail_" + find_patient_name_from_path(folder_path)
        detail_window, ind2 = find_window_by_type(type)
        # On récupère le chemin vers le dossier patient
        cut_folder_path = folder_path[:-len(find_last_part_from_path(folder_path))-1]
        #Puis on rafraichit
        refresh_detail_window_content(main_window, detail_window, cut_folder_path, history_file_path, labelBgColor="#808080", max_width=550)

        # On rafraichit aussi la fenêtre principale
        server_files_path = cut_folder_path[:-len(cut_folder_path.split('\\')[-1])-1]
        server_files_path.replace("\\\\", "\\")
        update_main_window(main_window, main_frame, server_files_path)

        destroy_path(os.path.join(abs_extract_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_extract_path, patientName))) == 0: destroy_path(os.path.join(abs_extract_path, patientName))
        destroy_path(os.path.join(abs_splitted_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_splitted_path, patientName))) == 0: destroy_path(os.path.join(abs_splitted_path, patientName))
        destroy_path(os.path.join(abs_optimized_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_optimized_path, patientName))) == 0: destroy_path(os.path.join(abs_optimized_path, patientName))
        destroy_path(os.path.join(abs_export_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_export_path, patientName))) == 0: destroy_path(os.path.join(abs_export_path, patientName))

        status_label_var.set("Succès")
        status_label.config(bg="green")
        optimization_is_launched = False
    else:
        status_label_var.set("Erreur")
        status_label.config(bg="red")
        optimization_is_launched = False
        destroy_path(os.path.join(abs_extract_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_extract_path, patientName))) == 0: destroy_path(os.path.join(abs_extract_path, patientName))
        destroy_path(os.path.join(abs_splitted_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_splitted_path, patientName))) == 0: destroy_path(os.path.join(abs_splitted_path, patientName))
        destroy_path(os.path.join(abs_optimized_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_optimized_path, patientName))) == 0: destroy_path(os.path.join(abs_optimized_path, patientName))
        destroy_path(os.path.join(abs_export_path, patientName, setup_name))
        if len(os.listdir(os.path.join(abs_export_path, patientName))) == 0: destroy_path(os.path.join(abs_export_path, patientName))

def browse_file(window, parent, folder_path, history_file_path):
    """
    Permet à l'utilisateur de parcourir et de sélectionner un fichier compressé (.zip) pour l'optimisation.

    Args:
        window (tk.Toplevel): La fenêtre d'extraction à fermer une fois la sélection effectuée.
        parent (tk.Toplevel): La fenêtre parent de la fenêtre d'extraction.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.

    Returns:
        None
    """
    file_types = [("Compressed files", "*.zip")]
    file_path = filedialog.askopenfilename(title="Parcourir...", filetypes=file_types)

    extract_path = get_global_variable("EXTRACT_FILES_TO")
    if extract_path is None:
        print("Le chemin d'extraction n'a pas été trouvé dans le fichier options.txt")
        return

    # Supprime le répertoire d'extraction et le recrée
    # if os.path.exists(extract_path):
    #     shutil.rmtree(extract_path)
    # os.makedirs(extract_path)

    abs_extract_path = os.path.abspath(extract_path)
    setup_name = folder_path.split('\\')[-1]
    patientName = folder_path.split('\\')[-2]
    recreate_directory(os.path.join(abs_extract_path, patientName))
    recreate_directory(os.path.join(abs_extract_path, patientName, setup_name))

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for zip_info in zip_ref.infolist():
            if not zip_info.is_dir():
                zip_info.filename = os.path.basename(zip_info.filename)
                zip_ref.extract(zip_info, os.path.join(abs_extract_path, patientName, setup_name))

    # print(f"Fichiers extraits vers : {extract_path}")

    # Ferme la fenêtre passée en paramètre
    window.destroy()

    # Ouvre une nouvelle fenêtre et lance le script d'optimisation d'objet
    open_obj_opt_window(parent, folder_path, history_file_path)


def display_uncompression_windows(parent, folder_path, history_file_path, labelBgColor="#808080", max_width=550):
    """
    Affiche une fenêtre pour permettre à l'utilisateur de parcourir et de sélectionner un fichier compressé (.zip) à décompresser.

    Args:
        parent (tk.Toplevel): La fenêtre parent de la fenêtre d'extraction.
        folder_path (str): Le chemin d'accès au dossier.
        history_file_path (str): Le chemin d'accès au fichier d'historique JSON.
        labelBgColor (str, optional): Couleur d'arrière-plan des labels. Par défaut : "#808080".
        max_width (int, optional): Largeur maximale de la fenêtre. Par défaut : 550.

    Returns:
        None
    """
    type = "uncompression_window_"+find_patient_name_from_path(folder_path)+"_"+os.path.basename(folder_path)

    if(find_window_by_type(type) == (None, 0)):
        detail_window = tk.Toplevel(parent)
        detail_window.title(f"{parent.title()} - {os.path.basename(folder_path)}")
        detail_window.iconbitmap('AF.ico')
        detail_window.configure(bg='#2b2b2b')

        add_window(type=type, window=detail_window)

        detail_window.columnconfigure(0, weight=1)
        detail_window.rowconfigure(0, weight=1)

        # Create a container frame to hold canvas and scrollbar
        container_frame = tk.Frame(detail_window)
        container_frame.pack(side='left', fill='both', expand=True)

        canvas = tk.Canvas(container_frame, bg='#2b2b2b')
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(container_frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Bind the mouse wheel event for scrolling
        def scroll_canvas(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            check_scroll_position(canvas)

        detail_window.bind("<MouseWheel>", scroll_canvas)

        detail_frame = tk.Frame(canvas, bg='#2b2b2b', padx=10, pady=0)
        canvas.create_window((0, 0), window=detail_frame, anchor='nw')

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        detail_frame.bind('<Configure>', update_scrollregion)

        # browse_button = tk.Button(detail_frame, text="Dossier manquant", command=browse_file)
        browse_button = create_styled_button(detail_frame, text="Parcourir...", width=150, height=50, button_color="ffffff", text_color="000000", radius = 5)
        browse_button.pack(pady=15)
        browse_button.bind('<Button-1>', lambda event, f=detail_window: browse_file(f, parent, folder_path, history_file_path))

        label_text = (
            "Advertising\n\n"
            "The landmarks file need to be .txt and named landmarks.txt\n"
            "The landmarks file need to be .txt and named IPR.csv\n"
            "The landmarks file need to be .txt and named Movement table.csv"
        )

        styled_label = create_styled_label(detail_frame, text=label_text, width=500, height=200)
        styled_label.pack()

        # Set the maximum width for the window
        detail_window.update_idletasks()
        content_height = detail_frame.winfo_reqheight()
        detail_window.maxsize(width=max_width, height=content_height)
        detail_window.geometry(str(max_width)+"x"+str(content_height))

        detail_window.protocol("WM_DELETE_WINDOW", lambda: close_window_and_remove_from_list(type))




def is_process_running(process_name, script_name):
    """
    Vérifie si un processus avec le nom donné et le script donné est en cours d'exécution.

    Args:
        process_name (str): Le nom du processus à vérifier.
        script_name (str): Le nom du script à vérifier.

    Returns:
        bool: True si le processus est en cours d'exécution, False sinon.
    """
    current_pid = os.getpid()
    for process in psutil.process_iter(['name', 'cmdline', 'pid']):
        if process.info['name'] == process_name and process.info['cmdline'] and process.info['pid'] != current_pid:
            for arg in process.info['cmdline']:
                if script_name in arg:
                    return True
    return False


if __name__ == "__main__":
    current_script_name = os.path.basename(__file__)
    if is_process_running("python.exe", current_script_name) or is_process_running("pythonw.exe", current_script_name):
        print("Erreur: interface.py est déjà en cours d'exécution.")
        sys.exit(1)
    else:
        server_files_path = get_server_files_path()
        if server_files_path:
            folders = [f for f in os.listdir(get_absolute_path(server_files_path)) if os.path.isdir(os.path.join(server_files_path, f))]
            create_interface(folders, server_files_path)
        else:
            print("Erreur: Le chemin d'accès n'a pas été trouvé dans le fichier options.txt.")
