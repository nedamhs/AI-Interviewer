## Table of Contents

Refer to the quickstart guide in the drive
- [About](#-about)
- [Setup](#-setup)
- [Running](#-running)

## About

**AI-Interviewer** is a project created by students of **UCI CS Capstone Project** and sponsored by **Pairwise AI**. The goal of this project is to create a base prototype of an AI-powered interviewer that can conduct basic early-stage screening interviews. This repository contains the source code for a basic prototype that can be ran on **Zoom**. The main goals of this project are:
- Create a working chat bot that can listen and talk over Zoom.
- Design and implement prompting techniques to create a curated interview for candidates.
- Create an easily integratable codebase

## Setup
This project requires **Docker** and the following required **environment variables**:
| Environmental Variable | Description |
| - | - |
| `OPENAI-API-KEY` | API key for accessing OpenAI API |
| `DEEPGRAM_API_KEY` | API key for accessing Deepgram transcription |
| `APP_CLIENT_ID` | Zoom App Client ID for accessing Zoom SDK |
| `APP_CLIENT_SECRET` | Zoom App Client Secret for accessing Zoom SDK |
| `REST_CLIENT_ID` | Zoom Server-To-Server OAuth credential used for accessing Zoom API |
| `REST_CLIENT_SECRET` | Zoom Server-To-Server OAuth credential used for accessing Zoom API |
| `REST_ACCOUNT_ID` | Zoom Server-To-Server OAuth credential used for accessing Zoom API |
After obtaining these variables, place them in a **.env** file in the main level directory. Obtaining the [OpenAI](https://openai.com/) and [Deepgram](https://deepgram.com/) API Keys can be done through their corresponding websites. Obtaining the Zoom credentials can be done through the [Zoom App Marketplace](https://marketplace.zoom.us/). After creating a Zoom account, create a **General App** by clicking **Develop** -> **Build App** -> **General App**. Make sure to enable **user:read:zak** in the Scopes. Make sure to also enable **Meeting SDK** in Embed. "After that, copy the **Client ID** and **Client Secret** of the app to your **APP_CLIENT_ID** and **APP_CLIENT_SECRET** environment variables. 

For the REST environment variables, create a **Server-To-Server OAuth** app in a similar way you would build the general app. Make sure to give your Server-To-Server App the **scopes** for all **Meeting** methods and **User** methods. Then, copy the corresponding variables to your .env file.

## Running

A Docker image is provided for deploying the Zoom chat bot on your own device. To run the Zoom container, first build:
```shell
docker compose build
```
To run:
```shell
docker compose run --rm develop
```
To run the chat bot as a text based conversation in your terminal, run:
```shell
python ai-interviewer/test_interview.py --terminal 
```