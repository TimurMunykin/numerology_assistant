
# Your Project Name

AI Expert is designed to create a "digital twin" of a real person by using a knowledge base to provide clear and accurate responses.

## Setup

To set up the project, follow these steps:

### Environment Variables Setup

1. In the root directory of the project, there is a file named `.env.template`. This file contains a template for the necessary environment variables.

2. Duplicate the `.env.template` file and rename it to `.env`.

   ```
   cp .env.template .env
   ```

3. Open the `.env` file in a text editor and update the environment variable values according to your requirements. For example:

   ```
   OPEN_AI_API_KEY=your_open_ai_api_key
   TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN
   OPEN_AI_GPT_MODEL=gpt-3.5-turbo-1106
   ```

   **Note:** The `.env` file is included in `.gitignore`, so it will not be committed to your Git repository.

## Running the Project

Run the project

```
python app.py
```

