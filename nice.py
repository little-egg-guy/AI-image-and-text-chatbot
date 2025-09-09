import os
import tkinter as tk
from tkinter import scrolledtext, font, ttk, messagebox
from PIL import Image, ImageTk
from openai import OpenAI
from huggingface_hub import InferenceClient
from threading import Thread

# Initialize the client with the Hugging Face Router API for TEXT
text_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN", "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")
)

# Initialize the client for IMAGE generation with featherless-ai provider
image_client = InferenceClient(
    provider="featherless-ai",  # Using featherless-ai provider
    api_key=os.getenv("HF_TOKEN", "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")
)

class MultiModelChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Model AI Assistant")
        self.root.geometry("800x800")
        self.root.configure(bg='#2b2b2b')
        
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful and friendly assistant."}
        ]
        
        self.setup_gui()
        
    def setup_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.image_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        
        self.notebook.add(self.chat_frame, text="💬 Chat")
        self.notebook.add(self.image_frame, text="🎨 Generate Image")
        
        self.setup_chat_tab()
        self.setup_image_tab()
        
    def setup_chat_tab(self):
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        chat_font = font.Font(family="Arial", size=11)
        
        title_label = tk.Label(
            self.chat_frame, 
            text="🤖 Text Chat Assistant", 
            font=title_font, 
            fg='#00ff00',
            bg='#2b2b2b'
        )
        title_label.pack(pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=chat_font,
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white'
        )
        self.chat_display.pack(pady=10, padx=20, fill='both', expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(self.chat_frame, bg='#2b2b2b')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        self.chat_input = tk.Entry(
            input_frame,
            font=font.Font(family="Arial", size=10),
            bg='#3b3b3b',
            fg='#ffffff',
            insertbackground='white'
        )
        self.chat_input.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        self.chat_input.bind('<Return>', self.send_chat_message)
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            bg='#00ff00',
            fg='#000000',
            font=('Arial', 10, 'bold')
        )
        send_button.pack(side=tk.RIGHT)
        
        self.add_chat_message("Assistant", "Hello! I can help you with text generation and create images from text. What would you like to do?", False)
    
    def setup_image_tab(self):
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        
        title_label = tk.Label(
            self.image_frame, 
            text="🎨 AI Image Generator", 
            font=title_font, 
            fg='#ff6b6b',
            bg='#2b2b2b'
        )
        title_label.pack(pady=10)
        
        model_frame = tk.Frame(self.image_frame, bg='#2b2b2b')
        model_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(model_frame, text="Image Model:", fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        
        # UPDATED: Models that work with featherless-ai provider
        self.image_model_var = tk.StringVar(value="runwayml/stable-diffusion-v1-5")
        model_dropdown = ttk.Combobox(
            model_frame,
            textvariable=self.image_model_var,
            values=[
                "runwayml/stable-diffusion-v1-5",      # Most reliable
                "stabilityai/stable-diffusion-2-1",    # Good alternative
                "CompVis/stable-diffusion-v1-4",       # Original version
                # These models are known to work well with featherless-ai
                "Lykon/dreamshaper-8",                 # Popular for artistic styles
                "SG161222/Realistic_Vision_V5.1",      # Good for photorealistic
            ],
            state="readonly",
            width=30
        )
        model_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        # Add info label about featherless-ai
        info_label = tk.Label(
            model_frame,
            text="(Using featherless-ai provider)",
            fg='#888888',
            bg='#2b2b2b',
            font=('Arial', 8)
        )
        info_label.pack(side=tk.RIGHT)
        
        prompt_frame = tk.Frame(self.image_frame, bg='#2b2b2b')
        prompt_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(prompt_frame, text="Describe your image:", fg='white', bg='#2b2b2b').pack(anchor='w')
        
        self.image_prompt = scrolledtext.ScrolledText(
            prompt_frame,
            height=4,
            font=font.Font(family="Arial", size=10),
            bg='#3b3b3b',
            fg='#ffffff',
            insertbackground='white'
        )
        self.image_prompt.pack(pady=5, fill='x')
        
        examples_frame = tk.Frame(self.image_frame, bg='#2b2b2b')
        examples_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Button(
            examples_frame,
            text="Astronaut riding a horse",
            command=lambda: self.set_prompt("Astronaut riding a horse on Mars, photorealistic, 4k"),
            bg='#3b3b3b',
            fg='#ffffff'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            examples_frame,
            text="Fantasy landscape",
            command=lambda: self.set_prompt("A magical forest with glowing mushrooms and fairies, fantasy art"),
            bg='#3b3b3b',
            fg='#ffffff'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            examples_frame,
            text="Cyberpunk city",
            command=lambda: self.set_prompt("Cyberpunk neon-lit cityscape at night with flying cars, rain-soaked streets"),
            bg='#3b3b3b',
            fg='#ffffff'
        ).pack(side=tk.LEFT)
        
        generate_btn = tk.Button(
            self.image_frame,
            text="✨ Generate Image",
            command=self.generate_image,
            bg='#ff6b6b',
            fg='#000000',
            font=('Arial', 12, 'bold'),
            pady=10
        )
        generate_btn.pack(pady=10)
        
        self.image_label = tk.Label(
            self.image_frame, 
            text="Your generated image will appear here", 
            bg='#1e1e1e',
            fg='#888888',
            font=('Arial', 10),
            wraplength=400
        )
        self.image_label.pack(pady=20, padx=20, fill='both', expand=True)
    
    def set_prompt(self, prompt):
        self.image_prompt.delete("1.0", tk.END)
        self.image_prompt.insert("1.0", prompt)
    
    def add_chat_message(self, sender, message, is_user=True):
        self.chat_display.config(state=tk.NORMAL)
        if is_user:
            self.chat_display.insert(tk.END, "You: ", 'user_tag')
        else:
            self.chat_display.insert(tk.END, "Assistant: ", 'assistant_tag')
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_chat_message(self, event=None):
        user_text = self.chat_input.get().strip()
        if not user_text:
            return
        
        self.chat_input.delete(0, tk.END)
        self.add_chat_message("You", user_text, True)
        self.conversation_history.append({"role": "user", "content": user_text})
        
        self.chat_input.config(state=tk.DISABLED)
        Thread(target=self.get_text_response, daemon=True).start()
    
    def get_text_response(self):
        try:
            completion = text_client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct-0905:together",
                messages=self.conversation_history,
                max_tokens=250,
                temperature=0.7,
            )
            
            assistant_reply = completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            self.root.after(0, lambda: self.show_text_response(assistant_reply))
            
        except Exception as e:
            self.root.after(0, lambda e=e: self.show_text_response(f"Error: {str(e)}"))
    
    def show_text_response(self, response):
        self.add_chat_message("Assistant", response, False)
        self.chat_input.config(state=tk.NORMAL)
        self.chat_input.focus()
    
    def generate_image(self):
        prompt = self.image_prompt.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter an image description")
            return
        
        selected_model = self.image_model_var.get()
        self.image_label.config(text=f"Generating image with {selected_model}...\nUsing featherless-ai provider...\nThis may take 15-30 seconds...")
        Thread(target=self.generate_image_thread, args=(prompt, selected_model), daemon=True).start()
    
    def generate_image_thread(self, prompt, model_name):
        try:
            # Use the clean text_to_image API with featherless-ai provider
            image = image_client.text_to_image(
                prompt,
                model=model_name,
            )
            
            # Resize for display
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            self.root.after(0, lambda: self.display_image(photo, prompt, model_name))
                
        except Exception as e:
            # Fixed error handling
            self.root.after(0, lambda e=e: self.image_label.config(text=f"Error: {str(e)}"))
    
    def display_image(self, photo, prompt, model_name):
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo
        
        self.add_chat_message("Assistant", f"Generated an image using {model_name} via featherless-ai based on: '{prompt}'", False)

def main():
    root = tk.Tk()
    app = MultiModelChatbotGUI(root)
    
    app.chat_display.tag_config('user_tag', foreground='#ff6b6b')
    app.chat_display.tag_config('assistant_tag', foreground='#4ecdc4')
    
    root.mainloop()

if __name__ == "__main__":
    main()