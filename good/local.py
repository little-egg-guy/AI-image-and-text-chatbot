import tkinter as tk
from tkinter import scrolledtext, ttk
import requests
import threading
import json
from datetime import datetime

# Modern color palette (Dark Theme)
BG_COLOR = "#0f1116"  # Dark blue-black
CARD_BG = "#1a1d25"   # Slightly lighter card background
ACCENT_COLOR = "#7e6cea"  # Purple accent
TEXT_PRIMARY = "#d84040"  # White text
TEXT_SECONDARY = "#9c2626"  # Gray text
USER_MSG_COLOR = "#7e6cea"  # Purple for user messages
BOT_MSG_COLOR = "#4a8fe7"   # Blue for bot messages
INPUT_BG = "#2a2f3b"       # Dark input background
BORDER_COLOR = "#2a2f3b"   # Border color

# Fonts
TITLE_FONT = ("Segoe UI Semibold", 18)
CHAT_FONT = ("Segoe UI", 12)
INPUT_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI Semibold", 10)

OLLAMA_URL = "http://localhost:11434/api/generate"

def get_ollama_response(prompt, model="llama3.1"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response.")
    except requests.exceptions.ConnectionError:
        return "🚫 Error: Cannot connect to Ollama. Please make sure it's running on localhost:11434"
    except requests.exceptions.Timeout:
        return "⏰ Error: Request timed out. The model might be taking too long to respond."
    except Exception as e:
        return f"❌ Error: {str(e)}"

class ModernChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(800, 600)
        
        # Configure styles
        self.setup_styles()
        
        # Main container with padding
        main_container = tk.Frame(root, bg=BG_COLOR, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = tk.Label(
            header_frame,
            text="🤖 AI Assistant",
            font=TITLE_FONT,
            fg=TEXT_PRIMARY,
            bg=BG_COLOR
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="● Online",
            font=("Segoe UI", 10),
            fg="#4ade80",  # Green for online
            bg=BG_COLOR
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Chat display area with card-like appearance
        chat_frame = tk.Frame(main_container, bg=CARD_BG, relief=tk.FLAT, bd=0)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        chat_frame.config(highlightbackground=BORDER_COLOR, highlightthickness=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=CHAT_FONT,
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for message styling
        self.setup_chat_tags()
        
        # Input area
        input_container = tk.Frame(main_container, bg=BG_COLOR)
        input_container.pack(fill=tk.X)
        
        # Input field with modern styling
        self.chat_input = tk.Text(
            input_container,
            font=INPUT_FONT,
            bg=INPUT_BG,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            height=3,
            wrap=tk.WORD,
            padx=15,
            pady=12,
            borderwidth=0
        )
        self.chat_input.pack(fill=tk.X, pady=(0, 10))
        self.chat_input.bind("<Return>", self.on_enter_pressed)
        self.chat_input.bind("<KeyPress>", self.on_key_press)
        
        # Button frame
        button_frame = tk.Frame(input_container, bg=BG_COLOR)
        button_frame.pack(fill=tk.X)
        
        # Clear chat button
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Chat",
            command=self.clear_chat,
            style="Modern.TButton"
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Send button with modern styling
        self.send_btn = ttk.Button(
            button_frame,
            text="🚀 Send Message",
            command=self.send_message,
            style="Accent.TButton"
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Set focus to input field
        self.chat_input.focus_set()
        
        # Welcome message
        self.root.after(1000, self.show_welcome_message)
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Modern.TButton",
                        font=BUTTON_FONT,
                        background=INPUT_BG,
                        foreground=TEXT_PRIMARY,
                        borderwidth=0,
                        focuscolor=ACCENT_COLOR)
        style.configure("Accent.TButton",
                        font=BUTTON_FONT,
                        background=ACCENT_COLOR,
                        foreground=TEXT_PRIMARY,
                        borderwidth=0)
        style.map("Accent.TButton",
                 background=[('active', USER_MSG_COLOR), ('pressed', USER_MSG_COLOR)])
    
    def setup_chat_tags(self):
        # User message styling
        self.chat_display.tag_config("user_msg", 
                                   foreground=USER_MSG_COLOR,
                                   font=("Segoe UI Semibold", 12),
                                   spacing1=5,
                                   spacing3=5)
        self.chat_display.tag_config("user_time", 
                                   foreground=TEXT_SECONDARY,
                                   font=("Segoe UI", 9))
        self.chat_display.tag_config("bot_msg", 
                                   foreground=BOT_MSG_COLOR,
                                   font=("Segoe UI Semibold", 12),
                                   spacing1=5,
                                   spacing3=5)
        self.chat_display.tag_config("bot_time", 
                                   foreground=TEXT_SECONDARY,
                                   font=("Segoe UI", 9))
        self.chat_display.tag_config("system_msg", 
                                   foreground=TEXT_SECONDARY,
                                   font=("Segoe UI Italic", 11))
    
    def on_enter_pressed(self, event):
        if event.state & 0x1:  # Shift+Enter for new line
            return
        else:
            self.send_message()
            return "break"
    
    def on_key_press(self, event):
        # Enable Ctrl+Enter to send
        if event.state & 0x4 and event.keysym == "Return":  # Ctrl+Enter
            self.send_message()
            return "break"
    
    def send_message(self):
        user_text = self.chat_input.get("1.0", tk.END).strip()
        if not user_text:
            return
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message("user", user_text)
        
        # Disable send button during processing
        self.send_btn.config(state="disabled")
        self.status_label.config(text="● Thinking...", fg="#fbbf24")  # Amber
        
        # Start response generation in thread
        threading.Thread(target=self.get_bot_response, args=(user_text,), daemon=True).start()
    
    def get_bot_response(self, user_message):
        bot_reply = get_ollama_response(user_message)
        
        # Update UI from main thread
        self.root.after(0, lambda: self.update_chat_display(bot_reply))
    
    def update_chat_display(self, bot_reply):
        self.add_message("bot", bot_reply)
        self.send_btn.config(state="normal")
        self.status_label.config(text="● Online", fg="#4ade80")  # Green
    
    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "user":
            self.chat_display.insert(tk.END, "👤 You ", "user_msg")
            self.chat_display.insert(tk.END, f"({timestamp})\n", "user_time")
            self.chat_display.insert(tk.END, f"{message}\n\n", "user_msg")
        else:
            self.chat_display.insert(tk.END, "🤖 Assistant ", "bot_msg")
            self.chat_display.insert(tk.END, f"({timestamp})\n", "bot_time")
            self.chat_display.insert(tk.END, f"{message}\n\n", "bot_msg")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def show_welcome_message(self):
        welcome_msg = "Hello! I'm your AI assistant. How can I help you today?"
        self.add_message("bot", welcome_msg)
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.show_welcome_message()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatbotGUI(root)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()