# Perplexity → OpenWebUI Converter

This repository contains Python scripts to convert **Perplexity Markdown chat exports** into **OpenWebUI-compatible JSON** files that you can directly import as conversations.

## Features

- Parse Perplexity Markdown export files (questions + answers).
- Clean output by removing:
  - Footnote-style citations (e.g. `[^1_1]`, `[^2_3]`).
  - Footnote definitions at the bottom of the file.
  - Hidden spans and decorative separators (logo, centered divider, etc.).
- Generate OpenWebUI JSON with:
  - Correct `history.messages` tree and `currentId`.
  - `parentId` / `childrenIds` links between messages.
  - Per-message timestamps, roles, and model metadata.
- Two conversion modes:
  - **One JSON per Q/A pair** (`convert_perplexity_v2.py`).
  - **Single threaded conversation** with all Q/A pairs (`convert_perplexity_thread.py`).

---

## Prerequisites

- Python 3.9+.
- A Perplexity export in **Markdown** (e.g. `exportPerplexity.md`).
- Your **OpenWebUI user ID** (used for the `userId` field in JSON).

---

## File Overview

- `convert_perplexity_v2.py`  
  Convert a Perplexity Markdown export into **multiple JSON files**, one per question/answer pair, each as a separate conversation in OpenWebUI.

- `convert_perplexity_thread.py`  
  Convert the same Markdown export into **a single conversation** containing the full chronological thread of all questions and answers.

---

## Usage

- `convert_perplexity_thread.py`  
  python3 convert_perplexity_thread.py Chat.md --userid "8e6a34b54s-2f4d-23-aa9b-1231fe788" --output-dir output

---

## Input Format (Perplexity Markdown)

The scripts expect a Perplexity export similar to:

```markdown
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" .../>

# Question 1 title

Answer text with explanations and citations like [^1_1][^1_2].

***

# Question 2 title

Another answer with citations and footnotes.

...

[^1_1]: https://example.com/link1
[^1_2]: https://example.com/link2
