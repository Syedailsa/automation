# Nova AI – Project Summary

**Nova AI** is an AI-powered learning platform that integrates **NotebookLM** with modern LLMs to provide an intelligent and seamless study experience.

Users sign in through **Google Authentication**, which automatically connects their **NotebookLM** account. They can then interact with their uploaded learning materials directly from the Nova AI dashboard.

For general questions, **LangChain** routes requests to **OpenRouter's Qwen models** to generate fast and accurate responses. When users request advanced learning resources such as **summaries, quizzes, study notes, FAQs, timelines, images, or podcasts**, the system uses **Playwright** to securely automate NotebookLM, generate the requested content, extract the results, and display them on the dashboard in real time.

### Tech Stack

* **Frontend:** PHP (Laravel)
* **Backend:** Python
* **AI Framework:** LangChain
* **LLM:** OpenRouter (Qwen Models)
* **Browser Automation:** Playwright
* **Authentication:** Google OAuth
* **Knowledge Generation:** NotebookLM

### Project Flow

1. User logs in using Google Authentication.
2. Nova AI automatically connects the user's NotebookLM account.
3. The user submits a query from the dashboard.
4. General queries are answered using **LangChain + OpenRouter (Qwen)**.
5. For content generation (Quiz, Summary, Notes, Images, Podcasts, etc.), **Playwright** automates NotebookLM to generate the requested output.
6. The generated content is extracted by the backend and displayed on the Nova AI dashboard for the user.
