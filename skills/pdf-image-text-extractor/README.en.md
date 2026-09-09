# PDF & Image Text Extractor / pdf-image-text-extractor

---

## Overview

Upload an image or PDF and automatically recognize and extract the text content within. It supports scanned-PDF recognition, structured table extraction, and batch directory processing, preserving the original structure and layout for clear, readable output.

**Core Value**

- **Instant recognition**: Upload an image or PDF—no extra steps needed, text extraction happens automatically.
- **Zero extra dependencies**: Scanned recognition and table extraction require no OCR engine or table library—ready to use out of the box.
- **Format preservation**: Paragraph structure and heading hierarchy are retained wherever possible, so results are ready to use.
- **Completely free**: Only a free API Key is needed for permission verification—no credits deducted.

**Intended Users**

- 📄 **Office workers** — Quickly extract text from scanned documents, contracts, and reports—no more manual retyping.
- 📊 **Finance / operations** — Turn PDF tables into Markdown in one click, ready to paste.
- 📚 **Students / researchers** — Pull content from academic PDFs for easier note-taking and citation.
- ✍️ **Content creators** — Grab text references from image assets to speed up your workflow.

---

## Features

### Core Capabilities

- **Image text extraction**: Upload an image to recognize all text within it—titles, body text, annotations, and more.
- **PDF text extraction**: Automatically parses text from PDF pages, processing multi-page documents in one pass.
- **Scanned-PDF recognition**: Automatically detects text-less scanned pages, renders them as high-resolution images, and recognizes them with AI vision—no OCR engine to install.
- **Structured table extraction**: Automatically recognizes tables in PDFs and outputs them as Markdown tables, preserving row and column structure.
- **Batch directory processing**: Pass in a directory path to process all PDF and image files inside in one go.
- **Structured output**: Results are presented in clean Markdown format for easy copying or exporting.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, confirm its source, scope of use, validity period, and whether it can be reset or revoked.
- Never hardcode or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language—no commands to memorize.

### Quick Reference

| Intent                     | Example phrase                                  | Result                                                          |
| -------------------------- | ----------------------------------------------- | --------------------------------------------------------------- |
| Extract text from an image | Upload an image and say "extract the text"      | Automatically recognizes and outputs all text in the image      |
| Extract text from a PDF    | Upload a PDF and say "convert this PDF to text" | Parses all pages and outputs with paragraph structure preserved |
| Recognize a scanned PDF    | Upload a scan and say "recognize this scanned document" | Renders scanned pages as images and recognizes the text |
| Extract PDF tables         | "Extract the tables from this PDF"              | Outputs structured Markdown tables, ready to paste              |
| Batch processing           | "Extract text from all files in this folder"    | Processes every PDF and image in the directory in one go        |
| Save extraction results    | "Save the extracted text"                       | Generates a Markdown file for later use                         |

### Output Example

After extraction, you'll see content similar to this:

```markdown
## Page 1

All the entanglements we've been through
And the regrets we've carried
None of it is meaningless

---

## Page 2

| Product | Units | Revenue |
| --- | --- | --- |
| Alpha | 1200 | 36000 |
| Beta | 860 | 25800 |
```

Multi-page PDFs are separated by `---` between pages; tables are output as standard Markdown tables.

---

## Use Cases

| Scenario              | Role                | Example question                                  | Benefit                                                        |
| --------------------- | ------------------- | ------------------------------------------------- | -------------------------------------------------------------- |
| Document digitization | Office worker       | "Turn this contract PDF into text"                | Skip manual retyping and digitize documents in seconds         |
| Scanned recognition   | Office / archivist  | "Recognize the text in this scanned document"     | No OCR software to install—AI recognizes it directly           |
| Table extraction      | Finance / operations| "Extract the tables from this report PDF"         | Get Markdown tables directly for easy downstream processing    |
| Archive management    | Individual user     | "Extract text from all files in this folder"      | Process a whole directory in one pass, saving time and effort  |
| Literature review     | Student / researcher| "Extract the content from this paper PDF"         | Makes note-taking, citation, and searching easier              |

---
