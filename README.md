# Customer Support System assisted by LLM (CuSupaLM)

## Description

This repository contains the source code for the Customer Support System assisted by LLM (CuSupaLM), a project developed
as part of the presentation session at the Google Developer Festival Yaoundé 2024. It contains the base code for all
components and concepts presented during the session except Streamlit, which is not yet added.

## Usage

### Copy the `settings_example.ini` file to `settings.ini` and fill it with your own values.

### Create your database and fill the settings in `settings.ini`

### Install the requirements dependencies

```
pip install -r requirements.txt
```

### Set up your Chroma server, I personally used this [resource](https://docs.trychroma.com/deployment/docker)

### Set up your Ollama server, I personally used this [resource](https://github.com/ollama/ollama)

## External dependencies tools

This project relies on [Ollama](https://ollama.com/), means that you can use it locally with any model you want.

It also relies on [Chroma](https://www.trychroma.com/) which is used as vector store, feel free to use what you want.

It also uses [LangSmith](https://smith.langchain.com/) to debug and trace our langchain chain, it can disable by
`LANGCHAIN_TRACING_V2 = true` in `settings.ini`