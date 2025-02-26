import os
import time
import watchdog.events
import watchdog.observers
import google.generativeai as genai
import customtkinter
from PIL import Image
import mimetypes
from threading import Thread

# --- Configuration ---

# Configure Gemini API Key (Replace with your actual key)
GOOGLE_API_KEY = "AIzaSyD1452xjuZaVWmkBnW8ac3eGy4pzSHfE_s"  # !!!  REPLACE THIS !!!
genai.configure(api_key=GOOGLE_API_KEY)

# Directories to monitor (Windows)
MONITORED_DIRECTORIES = [
    os.path.join(os.path.expanduser("~"), "Desktop"),
    os.path.join(os.path.expanduser("~"), "Documents"),
    os.path.join(os.path.expanduser("~"), "Downloads"),
    os.path.join(os.path.expanduser("~"), "Pictures"),
    # Add more directories as needed
]

# File extensions to analyze.  Key is the extension, value is the Gemini prompt
FILE_EXTENSIONS_TO_ANALYZE = {
    ".txt": "Assess the importance and summarize the content of this text document. Focus on key information, action items, and urgency. Provide a score between 1 (low importance) and 10 (high importance).",
    ".pdf": "Analyze this PDF document.  Determine its main topic, purpose, and importance.  Highlight any critical information, deadlines, or requests.  Assign an importance score from 1 (low) to 10 (high).",
    ".docx": "Evaluate the importance and summarize this Word document.  Identify key themes, action items, and any time-sensitive information. Provide a score between 1 (not important) and 10 (very important).",
    ".jpg": "Describe this image and assess its potential importance or relevance.  Consider if it contains important information, is related to a project, or has sentimental value. Score importance from 1 (low) to 10 (high).",
    ".jpeg": "Describe this image and assess its potential importance or relevance.  Consider if it contains important information, is related to a project, or has sentimental value. Score importance from 1 (low) to 10 (high).",
    ".png": "Describe this image and assess its potential importance. Is it a screenshot with important details, a design element for a project, or something else?  Score importance from 1 to 10.",
    ".img": "Describe this image and assess its potential importance. Is it a screenshot with important details, a design element for a project, or something else?  Score importance from 1 to 10.",  # You might need a more specific prompt if .img has a particular context in your use case
    # Add more extensions as needed
}

# --- Gemini AI Functions ---

def analyze_file_content(file_path, prompt):
    """Analyzes the content of a file using Gemini Pro or Gemini Pro Vision."""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        mime_type, _ = mimetypes.guess_type(file_path)

        if file_extension in (".jpg", ".jpeg", ".png", ".img"):
            # Use Gemini Pro Vision for image analysis
            model = genai.GenerativeModel('gemini-1.5-flash')
            image = Image.open(file_path)
            response = model.generate_content([prompt, image])
            return response.text

        elif file_extension in (".txt", ".pdf", ".docx"):
            # Use Gemini Pro for text analysis
            model = genai.GenerativeModel('gemini-1.5-flash')

            if file_extension == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()

            elif file_extension == ".pdf":  #Basic PDF support
                try:
                    import PyPDF2  #Try to import for PDF parsing.
                    with open(file_path, "rb") as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        file_content = ""
                        for page_num in range(len(pdf_reader.pages)):
                            file_content += pdf_reader.pages[page_num].extract_text()
                except ImportError:
                    return "PyPDF2 is not installed.  Unable to read PDF content. Install with 'pip install PyPDF2'"
                except Exception as e:
                    return f"Error reading PDF: {e}"
            elif file_extension == ".docx":  #Basic .docx support
                try:
                    import docx
                    doc = docx.Document(file_path)
                    file_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    return "python-docx is not installed. Unable to read .docx content. Install with 'pip install python-docx'"
                except Exception as e:
                    return f"Error reading .docx: {e}"

            if len(file_content) > 30000:  # Limit very large files
                file_content = file_content[:25000] + "\n... (truncated due to size) ..."

            response = model.generate_content(prompt + "\n\n" + file_content)
            return response.text


        else:
            return "Unsupported file type for analysis."


    except Exception as e:
        return f"Error analyzing file: {e}"


# --- File System Monitoring ---

class FileChangeHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def on_any_event(self, event):
      if event.is_directory:
          return None  # Ignore directory events

      file_path = event.src_path
      file_extension = os.path.splitext(file_path)[1].lower()

      if file_extension in FILE_EXTENSIONS_TO_ANALYZE:
          event_type = ""
          if event.event_type == watchdog.events.EVENT_TYPE_CREATED:
              event_type = "created"
          elif event.event_type == watchdog.events.EVENT_TYPE_MODIFIED:
              event_type = "modified"
          elif event.event_type == watchdog.events.EVENT_TYPE_MOVED:
            event_type = "moved"
          elif event.event_type == watchdog.events.EVENT_TYPE_DELETED:
              event_type = "deleted"
          else:
              event_type = "unknown"
          self.app.log_message(f"File {event_type}: {file_path}")
          print(f"File {event_type}: {file_path}")

          # Check if the file still exists before processing (handles quick deletes/moves)
          if event.event_type != watchdog.events.EVENT_TYPE_DELETED and os.path.exists(file_path):
                self.app.analyze_file(file_path)  # Call the analysis function
          else:
            self.app.log_message("file deleted/moved too fast")


# --- CustomTkinter GUI ---

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Monitor and Analyzer")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)


        # Left Panel:  File Event Log
        self.log_frame = customtkinter.CTkFrame(self)
        self.log_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        self.log_label = customtkinter.CTkLabel(self.log_frame, text="File Event Log", font=("Arial", 16))
        self.log_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        self.log_textbox = customtkinter.CTkTextbox(self.log_frame, wrap="word", state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")



        # Right Panel: Analysis Results
        self.analysis_frame = customtkinter.CTkFrame(self)
        self.analysis_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.analysis_frame.grid_rowconfigure(1, weight=1)
        self.analysis_frame.grid_columnconfigure(0, weight=1)

        self.analysis_label = customtkinter.CTkLabel(self.analysis_frame, text="Analysis Results", font=("Arial", 16))
        self.analysis_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        self.analysis_textbox = customtkinter.CTkTextbox(self.analysis_frame, wrap="word", state="disabled")
        self.analysis_textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Start Monitoring Button (Initially disabled until dependencies are checked)
        self.start_button = customtkinter.CTkButton(self, text="Start Monitoring", command=self.start_monitoring, state="disabled")
        self.start_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


        # ---  Dependency check and observer setup  ---
        self.observer = None
        self.check_dependencies()  # Run dependency check on startup
        self.setup_observer()



    def check_dependencies(self):
        """Checks for necessary libraries and API key."""
        missing_libs = []
        try:
            import watchdog
        except ImportError:
            missing_libs.append("watchdog")
        try:
            import google.generativeai
        except ImportError:
            missing_libs.append("google-generativeai")
        try:
             import PyPDF2
        except ImportError:
            missing_libs.append("PyPDF2")
        try:
             import docx
        except ImportError:
            missing_libs.append("python-docx")
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
            missing_libs.append("GEMINI_API_KEY")  # Treat missing API key as a dependency

        if missing_libs:
            error_message = "Missing dependencies:\n\n" + "\n".join(missing_libs)
            if "GEMINI_API_KEY" in missing_libs:
                error_message += "\n\nPlease set your GOOGLE_API_KEY in the script."
            else:
                error_message += "\n\nPlease install the missing libraries using:  pip install " + " ".join(missing_libs)

            self.log_message(error_message, error=True) # Log the error
            #You could also show a dialog box here if you prefer
            # customtkinter.CTkMessageBox(title="Error", message=error_message) #Doesn't seem to work on macos

        else:
            self.start_button.configure(state="normal")  # Enable the button
            self.log_message("Dependencies OK. Click 'Start Monitoring'")


    def setup_observer(self):
        """Sets up the file system observer."""
        if self.observer:
            self.observer.stop()  # Stop any existing observer
            self.observer.join()

        self.observer = watchdog.observers.Observer()
        event_handler = FileChangeHandler(self)
        for path in MONITORED_DIRECTORIES:
            if os.path.exists(path):
                self.observer.schedule(event_handler, path, recursive=True)
                self.log_message(f"Monitoring directory: {path}")
            else:
                self.log_message(f"Directory not found: {path}", error=True)

    def start_monitoring(self):
        """Starts the file system monitoring."""
        if self.observer and not self.observer.is_alive():
            try:
                self.observer.start()
                self.log_message("Monitoring started...")
                self.start_button.configure(text="Monitoring...", state="disabled") #Disable start button while running
            except RuntimeError as e:
                if "can't start new thread" in str(e):
                    self.log_message("Error: Too many threads. Try reducing the number of monitored directories.", error=True)
                else:
                    self.log_message(f"Error starting observer: {e}", error=True)


    def log_message(self, message, error=False):
        """Logs a message to the log textbox."""
        self.log_textbox.configure(state="normal")  # Enable editing
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")  # Disable editing
        self.log_textbox.see("end") # Scroll to the end

        if error:
            # You can add error highlighting here if you want
            pass



    def analyze_file(self, file_path):
        """Analyzes a file and updates the analysis textbox."""
        def run_analysis():
            file_extension = os.path.splitext(file_path)[1].lower()
            prompt = FILE_EXTENSIONS_TO_ANALYZE.get(file_extension)

            if prompt:
                self.analysis_textbox.configure(state="normal")
                self.analysis_textbox.delete("1.0", "end")
                self.analysis_textbox.insert("1.0", f"Analyzing {file_path}...\n")
                self.analysis_textbox.configure(state="disabled")

                result = analyze_file_content(file_path, prompt)

                self.analysis_textbox.configure(state="normal")
                self.analysis_textbox.delete("1.0", "end")  # Clear previous analysis
                self.analysis_textbox.insert("1.0", result)
                self.analysis_textbox.configure(state="disabled")
            else:
                self.log_message(f"No analysis configured for {file_extension} files.")

        # Run the analysis in a separate thread to avoid blocking the GUI
        analysis_thread = Thread(target=run_analysis)
        analysis_thread.start()



# --- Main Execution ---

if __name__ == "__main__":
    app = App()
    app.mainloop()