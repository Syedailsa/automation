class PromptTemplates:
    SYSTEM_PROMPT = """You are a NotebookLM automation assistant. 
You help users manage notebooks, sources, and generate outputs using natural language.
You can understand Roman Urdu and translate to English if needed."""

    ACTION_PLANNER_PROMPT = """Analyze the user input and determine the actions to perform.
    
User Input: {user_input}

Available actions:
- create_notebook: Create a new notebook
- add_source: Add a source to notebook
- generate_audio: Generate audio overview
- generate_video: Generate video overview
- generate_quiz: Generate quiz
- generate_flashcards: Generate flashcards
- generate_slides: Generate slide deck
- list_notebooks: List all notebooks

Return JSON with actions array."""

    ROMAN_URDU_TRANSLATOR = """Translate the following Roman Urdu to English:
    
{input}

Return only the English translation."""

    OUTPUT_FORMATTER = """Format the execution results into a readable message:

{results}"""
