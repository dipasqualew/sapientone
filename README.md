# Sapientone!

From the italian "Sapientone", you can ask ChatGPT what that means!

Sapientone brings GPT into your browser, via a Chrome Extension.

## Features

* Query ChatGPT via a Chrome Extension, by pressing CTRL+B
* Use memory (via Pinecone)

## Project

The monorepo is composed by:

* `./chrome`: Source code and build script for the Chrome Extension, using TS + Vue3 + Vite
* `./iac`: Infrastructure as Code, using TS + Pulumi
* `./lambdas`: Edge functions powering Sapientone, using Python + Google Cloud Functions
