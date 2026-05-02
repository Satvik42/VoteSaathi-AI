# VoteSaathi AI - Your Multilingual Election Companion

VoteSaathi AI is a polished, empathetic, and intelligent guide designed to help Indian voters navigate the complexities of the election system. Built with Flask, Vanilla JavaScript, and powered by Google Gemini API, it provides real-time assistance in multiple regional languages.

## Chosen Vertical: Indian Election Assistance & Voter Awareness

VoteSaathi AI addresses the critical need for accessible, multilingual information during elections, ensuring that every citizen—regardless of their primary language or technical proficiency—can exercise their right to vote with confidence.

## Approach and Logic

### 1. Dynamic Localization (Fix 1 & 2)
The application uses a robust JavaScript dictionary (`uiTranslations`) to instantly translate static UI elements (Welcome text, scenario cards, placeholders) when a user selects a language from the dropdown. This ensures zero latency and a seamless initial experience.

### 2. Intelligent Guided Mode
The "Guided Mode" takes users through a step-by-step wizard to identify their specific voting scenario (e.g., first-time voter, lost ID). The wizard is fully localized, updating questions and options in real-time based on the selected language.

### 3. Retroactive Chat Translation (Fix 4)
When a user changes the language mid-conversation, VoteSaathi AI doesn't just change the UI—it translates the *entire chat history*. It gathers existing messages, sends them to a specialized Flask route (`/translate_history`), and uses Gemini to translate the context accurately while preserving the flow.

### 4. Accessibility with Web Speech API (Fix 3)
To ensure accessibility, the app integrates the Web Speech API for both Speech-to-Text (STT) and Text-to-Speech (TTS). The microphone dynamically adjusts its recognition language to match the user's selection, allowing for hands-free querying in regional languages like Hindi, Tamil, Telugu, and Kannada.

### 5. Resilient Backend
The Flask backend implements a multi-model failover strategy. It prioritizes the latest Gemini models (like Gemini 3.1 Flash) for speed and cost-efficiency but can dynamically fall back to other available models if needed, ensuring high availability.

## How the Solution Works

1.  **Language Selection:** User selects their preferred language from the top-right dropdown.
2.  **Interaction:** User can either choose a pre-defined scenario (e.g., "I lost my Voter ID") or type/speak their own question.
3.  **Processing:** The query is sent to the Flask backend along with the selected language context.
4.  **AI Response:** Gemini processes the query and returns a structured JSON response containing a markdown-formatted answer and related follow-up suggestions.
5.  **Rendering:** The frontend renders the markdown and provides a "Read Aloud" option for better accessibility.

## Assumptions Made

- **API Connectivity:** The application assumes a stable internet connection for real-time interaction with the Gemini API.
- **Microphone Permissions:** STT functionality assumes the user grants microphone access in their browser.
- **Regional Dialects:** Recognition is optimized for standard regional language formats (e.g., `hi-IN`, `ta-IN`).

## How to Clone and Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Satvik42/VoteSaathi-AI.git
    cd VoteSaathi-AI
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your Gemini API Key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

5.  **Run the application:**
    ```bash
    python3 app.py
    ```
    Access the app at `http://127.0.0.1:5000`.
