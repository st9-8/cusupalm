## Customer Support System assisted by LLM (CuSupaLM)

### Description

This repository contains the source code for the Customer Support System assisted by LLM (CuSupaLM), a project developed
for the Google Developer Festival Yaoundé 2024 presentation session. It contains the base code for all
components and concepts presented during the session except Streamlit, which has not yet been added.

### Usage

1. Copy the `settings_example.ini` file to `settings.ini` and fill it with your own values.

2. Create your database and fill the settings in `settings.ini`

3. Install the requirements dependencies

  ```
  pip install -r requirements.txt
  ```

3. Set up your Chroma server, I used this [resource](https://docs.trychroma.com/deployment/docker)

4. Set up your Ollama server, I used this [resource](https://github.com/ollama/ollama)

### External dependencies tools

1. This project relies on [Ollama](https://ollama.com/), which means that you can use it locally with any model you want.
2. It also relies on [Chroma](https://www.trychroma.com/) which is used as vector store, feel free to use what you want.
3. It also uses [LangSmith](https://smith.langchain.com/) to debug and trace our langchain chain, it can be disabled by
`LANGCHAIN_TRACING_V2 = true` in `settings.ini`

### Architecture proposed

![CuSupaLM architecture](https://github.com/st9-8/cusupalm/blob/main/architecture.png)
