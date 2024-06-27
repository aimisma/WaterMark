from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk, TarIO

import os

# ---------------------------- CONSTANTS ------------------------------- #
DARKMARK = (68, 68, 68)
LIGHTMARK = (220, 220, 220)
FONT_NAME = os.path.join(os.path.dirname(__file__), "coolvetica rg it.otf")
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


img = None
img_tk = None
watermarked_img = None
selected_mode = None


# ---------------------------- MECHANISMS ------------------------------- #
#Resize the image to fit the window
def resize_image(event=None):
    global img, img_tk
    if img:
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height

        if canvas_ratio > img_ratio:
            new_height = canvas_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = canvas_width
            new_height = int(new_width / img_ratio)

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(resized_img)

        canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        canvas.create_image(x, y, anchor=NW, image=img_tk)

        initial_text_label.place_forget()


#Uploads picture to app
def upload():
    global img
    selected_file = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tar")]
    )
    if not selected_file:
        return
    if selected_file.lower().endswith('.tar'):
        fp = TarIO.TarIO(selected_file, os.path.basename(selected_file).replace('.tar', ''))
        img = Image.open(fp)
    else:
        img = Image.open(selected_file)
    resize_image()


#Creates a previsualization of the picture with the watermark.
def create_watermark(size, color, alpha=75):
    watermark = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)


    font_size = int(min(size) / 20)
    font = ImageFont.truetype(FONT_NAME, size=font_size)

    text = overlay_text_entry.get()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]


    x_repeat = (size[0] // text_width) + 1 if text_width > 0 else 1
    y_repeat = (size[1] // text_height) + 1 if text_height > 0 else 1

    for i in range(x_repeat):
        for j in range(y_repeat):
            draw.text((i * text_width, j * text_height), text, font=font, fill=color + (alpha,))

    return watermark


#Lets user pick between two modes of watermark and calls the previsualization.
def mode_selected():
    global img, img_tk, watermarked_img, selected_mode

    if not img:
        return

    selected_mode = var.get()
    if selected_mode == 1:
        watermark_color = LIGHTMARK
    elif selected_mode == 2:
        watermark_color = DARKMARK
    else:
        return

    watermark = create_watermark((img.width, img.height), watermark_color)
    watermarked_img = img.copy()
    watermarked_img.paste(watermark, (0, 0), mask=watermark)

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    img_ratio = watermarked_img.width / watermarked_img.height
    canvas_ratio = canvas_width / canvas_height

    if canvas_ratio > img_ratio:
        new_height = canvas_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = canvas_width
        new_height = int(new_width / img_ratio)

    img_tk = ImageTk.PhotoImage(watermarked_img.resize((new_width, new_height), Image.LANCZOS))

    canvas.delete("all")
    x = (canvas_width - new_width) // 2
    y = (canvas_height - new_height) // 2
    canvas.create_image(x, y, anchor=NW, image=img_tk)

    initial_text_label.place_forget()



#Applies the watermark to a copy of the original picture and let's user save it
def confirm():
    global img, selected_mode

    if not img:
        return

    selected_mode = var.get()
    if selected_mode == 1:
        watermark_color = LIGHTMARK
    elif selected_mode == 2:
        watermark_color = DARKMARK
    else:
        return


    watermark = create_watermark((img.width, img.height), watermark_color)
    img_with_watermark = img.copy()
    img_with_watermark.paste(watermark, (0, 0), mask=watermark)

    save_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(img.filename)[1],
                                             filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                        ("GIF files", "*.gif"), ("BMP files", "*.bmp"),
                                                        ("TIFF files", "*.tiff")])
    if save_path:
        img_with_watermark.save(save_path)


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Watermark")
window.minsize(width=700, height=500)

window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create a Frame for the Canvas in which the picture will be shown
canvas_frame = Frame(window)
canvas_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Allow the frame to expand
canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(0, weight=1)

# -------------------- Canvas ------------------
canvas = Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.grid(row=0, column=0, sticky="nsew")

initial_text_label = Label(canvas, text="Image will appear here", font=(FONT_NAME, 20), bg="white")
initial_text_label.place(relx=0.5, rely=0.5, anchor=CENTER)

canvas.bind("<Configure>", resize_image)

# ---------------------Buttons-------------------
# --------Upload Picture------
upload = Button(text="Upload Picture", command=upload, font=(FONT_NAME, 12))
upload.grid(row=0, column=0, padx=10)

# ------- Select Mode------
var = IntVar()
light_button = Radiobutton(window, text="Light Mark", variable=var, value=1, command=mode_selected)
dark_button = Radiobutton(window, text="Dark Mark", variable=var, value=2, command=mode_selected)
light_button.grid(row=0, column=1)
dark_button.grid(row=0, column=2)

# ------- Watermark Text Entry -----
overlay_text_entry = Entry(window, width=30, font=(FONT_NAME, 12))
overlay_text_entry.grid(row=0, column=3, padx=10)
overlay_text_entry.insert(0, "Your Watermark Here")

# -------Confirm and save -----
confirm = Button(text="Save", command=confirm, font=(FONT_NAME, 12))
confirm.grid(row=3, column=2, padx=10, pady=10, sticky='se')

window.mainloop()