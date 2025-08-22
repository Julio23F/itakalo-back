"""
Fichier: style.py

Ce fichier contient des fonctions permettant de créer des widgets personnalisés pour l'interface utilisateur
tels que des boutons, des labels et des champs de texte avec des styles personnalisés, des formes arrondies
et des couleurs spécifiées.

Auteur : Robin Lasserye
Date : 15/04/2023
Version : 1
"""
from PIL import Image, ImageDraw, ImageTk
from tkinter import ttk
import tkinter as tk


def lerp_color(color1, color2, t):
    """
    Interpole linéairement entre deux couleurs RGB en fonction de la valeur de t.

    Args:
        color1 (tuple): La première couleur RGB sous forme de tuple (r, g, b).
        color2 (tuple): La seconde couleur RGB sous forme de tuple (r, g, b).
        t (float): Le paramètre d'interpolation, compris entre 0 et 1.

    Returns:
        tuple: La couleur RGB interpolée sous forme de tuple (r, g, b).
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return int(r1 + t * (r2 - r1)), int(g1 + t * (g2 - g1)), int(b1 + t * (b2 - b1))


def create_styled_button(parent, text, width, height, button_color="ff0000", command=None, radius = 15, text_color="ffffff"):
    """
    Crée et retourne un bouton stylisé avec les paramètres donnés.

    Args:
        parent (tk.Widget): Le widget parent du bouton.
        text (str): Le texte à afficher sur le bouton.
        width (int): La largeur du bouton en pixels.
        height (int): La hauteur du bouton en pixels.
        button_color (str): La couleur du bouton au format hexadécimal (ex: "00ff00" pour vert).
        command (callable, optional): La fonction à appeler lorsqu'on clique sur le bouton.
        radius (int, optional): Le rayon des coins arrondis du bouton en pixels.
        text_color (str, optional): La couleur du texte au format hexadécimal (ex: "00ff00" pour vert).

    Returns:
        tk.Button: Le bouton stylisé créé.
    """
    button_color = tuple(int(button_color[i:i+2], 16) for i in (0, 2, 4))  # Convert button_color to RGB tuple
    button_color_darker = lerp_color(button_color, (0, 0, 0), 0.15)  # Darken the color by 15%
    button_color_hex = '#%02x%02x%02x' % button_color  # Convert RGB tuple back to HEX
    button_color_darker_hex = '#%02x%02x%02x' % button_color_darker  # Convert RGB tuple back to HEX

    button_image_normal = create_rounded_rect(width, height, radius, button_color_hex)
    button_image_active = create_rounded_rect(width, height, radius, button_color_darker_hex)
    button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)
    button_image_active_tk = ImageTk.PhotoImage(button_image_active)


    button = tk.Button(parent, text=text, width=width, height=height, fg="#"+text_color, font=('Arial', 10, 'bold'), image=button_image_normal_tk, compound=tk.CENTER, relief=tk.FLAT, padx=0, pady=0, bg='#2b2b2b', activebackground='#2b2b2b', bd=0)
    button.image_normal = button_image_normal_tk
    button.image_active = button_image_active_tk

    button.bind('<Enter>', lambda event, btn=button: btn.config(image=button_image_active_tk))
    button.bind('<Leave>', lambda event, btn=button: btn.config(image=button_image_normal_tk))

    return button


def create_styled_label(parent, text, width, height, label_color="ffffff", text_color="ffffff"):
    """
    Crée un label personnalisé avec un arrière-plan arrondi et une couleur de texte spécifiée.

    Args:
        parent (Tkinter.Widget): Le widget parent auquel le label sera attaché.
        text (str): Le texte à afficher sur le label.
        width (int): La largeur du label en pixels.
        height (int): La hauteur du label en pixels.
        label_color (str, optional): La couleur de l'arrière-plan du label au format hexadécimal (sans le préfixe #). Par défaut "ffffff".
        text_color (str, optional): La couleur du texte au format hexadécimal (sans le préfixe #). Par défaut "ffffff".

    Returns:
        Tkinter.Label: Le label personnalisé créé.
    """
    radius = 15

    label_image_normal = create_rounded_rect(width, height, radius, "#" + label_color)
    label_image_normal_tk = ImageTk.PhotoImage(label_image_normal)

    label = tk.Label(parent, text=text, width=width, height=height, fg="#"+text_color, font=('Arial', 10, 'bold'), image=label_image_normal_tk, compound=tk.CENTER, relief=tk.FLAT, padx=0, pady=0, bg='#2b2b2b', activebackground='#2b2b2b', bd=0)

    return label



def create_styled_entry(parent, width, height, textvariable, entry_color="ffffff", text_color="ffffff"):
    """
    Crée un Entry personnalisé avec un arrière-plan arrondi et une couleur de texte spécifiée.

    Args:
        parent (Tkinter.Widget): Le widget parent auquel le Entry sera attaché.
        width (int): La largeur de l'Entry en pixels.
        height (int): La hauteur de l'Entry en pixels.
        entry_color (str, optional): La couleur de l'arrière-plan du Entry au format hexadécimal (sans le préfixe #). Par défaut "ffffff".
        text_color (str, optional): La couleur du texte au format hexadécimal (sans le préfixe #). Par défaut "ffffff".

    Returns:
        Tkinter.Entry: Le Entry personnalisé créé.
    """

    radius = 15
    style = ttk.Style()
    style_name = "Custom.Entry"
    style.configure(style_name, background="#2b2b2b", fieldbackground=entry_color, foreground=text_color, font=('Arial', 10, 'bold'))

    entry_image_normal = create_rounded_rect(width, height, radius, "#" + entry_color)
    entry_image_normal_tk = ImageTk.PhotoImage(entry_image_normal)

    entry_label = tk.Label(parent, image=entry_image_normal_tk, bg="#2b2b2b")
    entry_label.image = entry_image_normal_tk
    entry_label.place(x=0, y=0)

    entry = ttk.Entry(parent, style=style_name, width=width, textvariable=textvariable)
    entry.place(x=radius, y=round(height/2))

    return entry


def lerp(a, b, t):
    """
    Interpole linéairement entre deux valeurs en fonction de la valeur de t.

    Args:
        a (float): La première valeur.
        b (float): La seconde valeur.
        t (float): Le paramètre d'interpolation, compris entre 0 et 1.

    Returns:
        float: La valeur interpolée.
    """
    return a + (b - a) * t


def darker_color(color, t=0.1):
    """
    Assombrit une couleur donnée en fonction de la valeur de t.

    Args:
        color (str): La couleur au format hexadécimal (ex: "#00ff00" pour vert).
        t (float, optional): Le paramètre d'assombrissement, compris entre 0 et 1. Par défaut 0.1.

    Returns:
        str: La couleur assombrie au format hexadécimal (ex: "#00ff00" pour vert).
    """
    r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    r, g, b = (int(lerp(c, 0, t)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


# Function to create a rounded rectangle image
def create_rounded_rect(width, height, radius, color):
    """
    Crée une image de rectangle arrondi avec les dimensions et la couleur spécifiées.

    Args:
        width (int): La largeur du rectangle en pixels.
        height (int): La hauteur du rectangle en pixels.
        radius (int): Le rayon des coins arrondis en pixels.
        color (str): La couleur du rectangle au format hexadécimal (ex: "#00ff00" pour vert).

    Returns:
        PIL.Image.Image: L'image du rectangle arrondi créée.
    """
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (radius, 0, width - radius, height),
        fill=color,
    )
    draw.rectangle(
        (0, radius, width, height - radius),
        fill=color,
    )
    draw.pieslice(
        (0, 0, radius * 2, radius * 2),
        180,
        270,
        fill=color,
    )
    draw.pieslice(
        (width - radius * 2, 0, width, radius * 2),
        270,
        0,
        fill=color,
    )
    draw.pieslice(
        (0, height - radius * 2, radius * 2, height),
        90,
        180,
        fill=color,
    )
    draw.pieslice(
        (width - radius * 2, height - radius * 2, width, height),
        0,
        90,
        fill=color,
    )

    return image

def create_rounded_rect_with_circle(width, height, radius, color, small_circle=False):
    """
    Crée une image de rectangle arrondi avec les dimensions et la couleur spécifiées et optionnellement un petit cercle.

    Args:
        width (int): La largeur du rectangle en pixels.
        height (int): La hauteur du rectangle en pixels.
        radius (int): Le rayon des coins arrondis en pixels.
        color (str): La couleur du rectangle au format hexadécimal (ex: "#00ff00" pour vert).
        small_circle (bool, optional): Si True, un petit cercle sera ajouté en bas à droite du rectangle. Par défaut False.

    Returns:
        PIL.Image.Image: L'image du rectangle arrondi créée.
    """
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (radius, 0, width - radius, height),
        fill=color,
    )
    draw.rectangle(
        (0, radius, width, height - radius),
        fill=color,
    )
    draw.pieslice(
        (0, 0, radius * 2, radius * 2),
        180,
        270,
        fill=color,
    )
    draw.pieslice(
        (width - radius * 2, 0, width, radius * 2),
        270,
        0,
        fill=color,
    )
    draw.pieslice(
        (0, height - radius * 2, radius * 2, height),
        90,
        180,
        fill=color,
    )
    draw.pieslice(
        (width - radius * 2, height - radius * 2, width, height),
        0,
        90,
        fill=color,
    )

    if small_circle:
        circle_radius = 6
        circle_x = width - circle_radius * 2
        circle_y = height - circle_radius * 2
        draw.ellipse([circle_x, circle_y, circle_x + circle_radius * 2, circle_y + circle_radius * 2], fill="red")

    return image