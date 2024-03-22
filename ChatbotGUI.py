import json
import tkinter as tk
from tkinter import ttk, messagebox
import requests

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = 'spyy/x'  # TODO: update this for whatever model you wish to use

class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MyTourguide")

        # Set the title bar text color to white
        self.root.tk_setPalette(background='#333333', foreground='white')

        self.style = ttk.Style()
        self.style.theme_use("clam")  # Change the theme as per your preference

        # Set the background and foreground colors for the application
        self.root.configure(bg="#333333")

        # Set a modern font and make all text bold
        bold_font = ("Helvetica", 10, "bold")

        self.history_text = tk.Text(self.root, wrap=tk.WORD, height=15, width=80, font=bold_font, bg="#222222", fg="white")
        self.history_text.pack(pady=(20, 10), padx=20, fill=tk.BOTH, expand=True)

        self.input_frame = ttk.Frame(self.root, style="Input.TFrame")
        self.input_frame.pack(pady=10, padx=20, fill=tk.X)

        self.input_text = ttk.Entry(self.input_frame, width=80, font=bold_font, style="Input.TEntry")
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_button = ttk.Button(self.input_frame, text="➔", command=self.generate_text, style="Send.TButton")
        self.send_button.pack(side=tk.LEFT, padx=(10, 0))

        # Custom Style Configuration
        self.style.configure("Input.TFrame", background="#333333")
        self.style.configure("Input.TEntry", background="black", foreground="black")
        self.style.configure("Send.TButton", background="#4da6ff", foreground="white", padding=5)
        self.history_text.tag_configure("response", foreground="green")

        self.context = []  # Initialize conversation history

    def generate_text(self):
        prompt = self.input_text.get().strip()
        if prompt:
            try:
                generated_text, self.context = self.generate(prompt, self.context)  # Update context with new response
                self.add_to_history("You: " + prompt)
                self.add_to_history("\nTourguide: " + generated_text + "\n\n")  # Changed "Bot" to "Tourguide"
                self.input_text.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please enter a prompt.")

    def generate(self, prompt, context):
        r = requests.post('http://localhost:11434/api/generate',
                          json={
                              'model': model,
                              'prompt': prompt,
                              'context': context,
                          },
                          stream=True)
        r.raise_for_status()

        generated_text = ''
        for line in r.iter_lines():
            body = json.loads(line)
            response_part = body.get('response', '')
            # Append the response to the generated text
            generated_text += response_part

            if 'error' in body:
                raise Exception(body['error'])

            if body.get('done', False):
                return generated_text, body['context']  # Return generated text along with updated context

    def add_to_history(self, message):
        # Check if the message starts with "Tourguide:"
        if message.startswith("\nTourguide:"):
            # Apply the "response" tag to the generated response only
            self.history_text.insert(tk.END, message[:11], "normal")  # Add "Tourguide:" without color
            self.history_text.insert(tk.END, message[11:],
                                     "response")  # Apply green color to the generated response
        else:
            # Insert the message normally without any color formatting
            self.history_text.insert(tk.END, message + "\n")
        self.history_text.see(tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ChatGUI()
    app.run()
