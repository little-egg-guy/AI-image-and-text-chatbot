import os
import tempfile
import pygame
import sys
import requests
from threading import Thread
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
from huggingface_hub import InferenceClient
import json

import sys
import requests
from threading import Thread
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
from huggingface_hub import InferenceClient
import json

# --- Restored Constants ---
ACCENT_COLOR = '#2cb67d'
INPUT_FONT = ('Segoe UI', 11)
BG_COLOR = '#18181b'
CHAT_BG = '#23232a'
INPUT_BG = '#23232a'
USER_COLOR = '#ff5c57'
ASSISTANT_COLOR = '#57c7ff'
TITLE_FONT = ('Segoe UI', 18, 'bold')
CHAT_FONT = ('Segoe UI', 12)
IMAGE_MODEL = "ByteDance/SDXL-Lightning"
TITLE_FONT = ("Segoe UI", 18, "bold")
CHAT_FONT = ("Segoe UI", 12)

# --- Tokens (for image/video only) ---
HF_TOKEN = "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"  # For image/video generation


class MultiModelChatbotGUI:
    def setup_gui(self):
        # Create main frame
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Chat tab
        self.chat_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.chat_frame, text="💬 Chat (Local)")

        # Image tab
        self.image_frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.image_frame, text="🎨 Generate Image")

        # Setup chat tab UI
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=CHAT_FONT,
            bg=CHAT_BG,
            fg='#ffffff',
            insertbackground='white'
        )
        self.chat_display.pack(pady=10, padx=20, fill='both', expand=True)
        self.chat_display.config(state=tk.DISABLED)

        input_frame = tk.Frame(self.chat_frame, bg=BG_COLOR)
        input_frame.pack(pady=10, padx=20, fill='x')

        self.chat_input = tk.Entry(
            input_frame,
            font=INPUT_FONT,
            bg=INPUT_BG,
            fg='#e0e0e0',
            insertbackground=ACCENT_COLOR,
            relief='flat',
            highlightthickness=2,
            highlightbackground=ACCENT_COLOR,
            borderwidth=8
        )
        self.chat_input.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', self.send_chat_message)

        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            bg=ACCENT_COLOR,
            fg=BG_COLOR,
            font=INPUT_FONT,
            relief='flat',
            activebackground=USER_COLOR,
            activeforeground='#fff',
            borderwidth=0,
            padx=16,
            pady=8
        )
        send_button.pack(side=tk.RIGHT)

        # Setup image tab UI
        image_container = tk.Frame(self.image_frame, bg=BG_COLOR)
        image_container.pack(fill='both', expand=True)

        self.image_prompt = scrolledtext.ScrolledText(
            image_container,
            height=4,
            font=INPUT_FONT,
            bg=INPUT_BG,
            fg='#e0e0e0',
            insertbackground=ACCENT_COLOR,
            relief='flat',
            borderwidth=8
        )
        self.image_prompt.pack(pady=5, fill='x')

        generate_btn = tk.Button(
            image_container,
            text="⚡ Generate with SDXL-Lightning",
            command=self.generate_image,
            bg=USER_COLOR,
            fg='#fff',
            font=("Segoe UI", 13, "bold"),
            relief='flat',
            activebackground=ACCENT_COLOR,
            activeforeground=BG_COLOR,
            borderwidth=0,
            padx=18,
            pady=10
        )
        generate_btn.pack(pady=10)

        self.image_label = tk.Label(
            image_container,
            text=f"Images will be generated using {IMAGE_MODEL} via fal-ai",
            bg=CHAT_BG,
            fg='#888888',
            font=("Arial", 10),
            wraplength=400,
            height=10
        )
        self.image_label.pack(pady=20, padx=20, fill='both', expand=True)
    """Multi-Model AI Assistant GUI supporting text (via local Ollama), image, and video generation."""
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Model AI Assistant (Local Ollama)")
        self.root.geometry("1500x1300")
        self.root.configure(bg=BG_COLOR)

        self.conversation_history = [
            {"role": "system", "content": "You are a helpful and friendly assistant."}
        ]
        self.last_generated_image = None
        self.selected_image = None

        if not HF_TOKEN:
            messagebox.showwarning("Warning", "HF_TOKEN environment variable not set. Hugging Face video generation will not work.")

        self.setup_gui()




    def _add_label(self, frame, text, fg, font=None, pady=0, wraplength=None, anchor=None, side=None, padx=None):
        """Helper to add a label to a frame."""
        kwargs = {"text": text, "fg": fg, "bg": BG_COLOR}
        if font:
            kwargs["font"] = font
        if wraplength:
            kwargs["wraplength"] = wraplength
        if anchor:
            kwargs["anchor"] = anchor
        label = tk.Label(frame, **kwargs)
        if side:
            label.pack(side=side, padx=padx if padx else 0)
        else:
            label.pack(pady=pady)
        return label
    
    def set_prompt(self, prompt):
        """Set the image prompt text."""
        self.image_prompt.delete("1.0", tk.END)
        self.image_prompt.insert("1.0", prompt)
    
    def set_video_prompt(self, prompt):
        """Set the video prompt text."""
        self.video_prompt.delete("1.0", tk.END)
        self.video_prompt.insert("1.0", prompt)
    
    def add_chat_message(self, sender, message, is_user=True):
        """Add a chat message to the display."""
        self.chat_display.config(state=tk.NORMAL)
        tag = 'user_tag' if is_user else 'assistant_tag'
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_chat_message(self, event=None):
        """Handle sending a chat message."""
        user_text = self.chat_input.get().strip()
        if not user_text:
            return

        self.chat_input.delete(0, tk.END)
        self.add_chat_message("You", user_text, True)
        self.conversation_history.append({"role": "user", "content": user_text})

        self.chat_input.config(state=tk.DISABLED)
        Thread(target=self.get_text_response, daemon=True).start()
    
    def get_text_response(self):
        """Get response from Hugging Face router API using OpenAI client."""
        try:
            import os
            from openai import OpenAI

            # Prepare messages for the API
            messages = self.conversation_history[-2:] if len(self.conversation_history) >= 2 else self.conversation_history
            # Format messages for OpenAI API
            formatted_messages = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                formatted_messages.append({"role": role, "content": content})

            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=HF_TOKEN,
            )
            completion = client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905:together",
                messages=formatted_messages,
            )
            assistant_reply = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            self.root.after(0, lambda: self.show_text_response(assistant_reply))
        except Exception as e:
            self.root.after(0, lambda: self.show_text_response(f"Hugging Face API error: {str(e)}"))
    
    def show_text_response(self, response):
        """Show assistant's response in chat."""
        self.add_chat_message("Assistant", response, False)
        self.chat_input.config(state=tk.NORMAL)
        self.chat_input.focus()
    
    def generate_image(self):
        """Start image generation thread."""
        prompt = self.image_prompt.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter an image description")
            return
        self.image_label.config(text=f"Generating image with {IMAGE_MODEL}...\nUsing fal-ai provider...\nThis should be fast!")
        Thread(target=self.generate_image_thread, args=(prompt,), daemon=True).start()
    
    def generate_image_thread(self, prompt):
        """Generate image using Hugging Face API and update GUI."""
        try:
            client = InferenceClient(api_key=HF_TOKEN)
            image = client.text_to_image(prompt, model=IMAGE_MODEL)
            self.last_generated_image = image.copy()
            self.selected_image = self.last_generated_image
            # Resize for display
            original_width, original_height = image.size
            max_size = 400
            if original_width > original_height:
                new_width = max_size
                new_height = int(original_height * (max_size / original_width))
            else:
                new_height = max_size
                new_width = int(original_width * (max_size / original_height))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.root.after(0, lambda: self.display_image(photo, prompt))
        except Exception as e:
            self.root.after(0, lambda e=e: self.image_label.config(text=f"Error: {str(e)}"))
    
    def display_image(self, photo, prompt):
        """Display generated image and update chat."""
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
        self.add_chat_message("Assistant", f"Generated an image based on: '{prompt}'", False)
    

def main():
    """Run the Multi-Model Chatbot GUI."""
    root = tk.Tk()
    app = MultiModelChatbotGUI(root)
    app.chat_display.tag_config('user_tag', foreground=USER_COLOR)
    app.chat_display.tag_config('assistant_tag', foreground=ASSISTANT_COLOR)
    root.mainloop()

if __name__ == "__main__":
    main()