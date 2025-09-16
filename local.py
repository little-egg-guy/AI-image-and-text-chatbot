
import tkinter as tk
from tkinter import scrolledtext
import requests

# Modern UI colors and fonts
BG_COLOR = '#18181b'
ACCENT_COLOR = '#2cb67d'
CHAT_BG = '#23232a'
USER_COLOR = '#ff5c57'
BOT_COLOR = '#57c7ff'
INPUT_BG = '#23232a'
INPUT_FONT = ('Segoe UI', 14)
CHAT_FONT = ('Segoe UI', 16)

OLLAMA_URL = "http://localhost:11434/api/generate"  # Correct Ollama endpoint

def get_ollama_response(prompt, model="llama3.1"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response.")
    except Exception as e:
        return f"Error: {e}"


class OllamaChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Local Chatbot")
        self.root.geometry("700x600")
        self.root.configure(bg=BG_COLOR)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=CHAT_FONT,
            bg=CHAT_BG,
            fg='#ffffff',
            insertbackground=ACCENT_COLOR,
            relief='flat',
            borderwidth=0
        )
        self.chat_display.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Input frame
        self.input_frame = tk.Frame(root, bg=BG_COLOR)
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)

        self.chat_input = tk.Text(
            self.input_frame,
            font=INPUT_FONT,
            bg=INPUT_BG,
            fg='#e0e0e0',
            insertbackground=ACCENT_COLOR,
            relief='flat',
            highlightthickness=2,
            highlightbackground=ACCENT_COLOR,
            borderwidth=8,
            height=8,
            wrap=tk.WORD,
            padx=12,
            pady=8
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=8)
        self.chat_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
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
        self.send_button.pack(side=tk.RIGHT)

        # Set focus to input field on startup
        self.chat_input.focus_set()

        # Conversation history for memory
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def send_message(self, event=None):
        user_text = self.chat_input.get("1.0", tk.END).strip()
        if not user_text:
            return
        self.append_message("You", user_text)
        self.chat_input.delete("1.0", tk.END)
        self.chat_input.focus_set()
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_text})
        self.root.after(100, self.get_bot_response)

    def get_bot_response(self):
        # Send only the latest user message to Ollama /generate
        last_user_message = self.conversation_history[-1]["content"] if self.conversation_history else ""
        payload = {
            "model": "llama3.1",
            "prompt": last_user_message,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            print("Ollama raw response:", data)  # Debug print
            bot_reply = data.get("response", "No response.")
            self.conversation_history.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            bot_reply = f"Error: {e}"
        self.append_message("Ollama", bot_reply)

    def append_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        tag = 'user_tag' if sender == "You" else 'bot_tag'
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        # Tag colors
        self.chat_display.tag_config('user_tag', foreground=USER_COLOR, font=CHAT_FONT)
        self.chat_display.tag_config('bot_tag', foreground=BOT_COLOR, font=CHAT_FONT)

if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaChatbotGUI(root)
    root.mainloop()