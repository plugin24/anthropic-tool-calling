## How to run this PoC - 

1. Install Requirements

    `
    pip install -r requirements.txt
    `
2. Create a `.env` file, and store your Anthropic API key. (ANTHROPIC_API_KEY="")

3. Run poc_1.py file

    `
    python -u poc_1.py
    `

## PoC Structure - 

- Prompts
    - general_prompt.py (A simple system prompt)

- Tools
    - anthropic_tools.py (All tools are defined here)

- poc_1.py (Main execution file)

- README.md (You are reading me right now)

- requirements.txt (All project requirements)