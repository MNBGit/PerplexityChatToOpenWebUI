#!/usr/bin/env python3
"""
Convertisseur Export Perplexity vers JSON OpenWebUI (Fil de discussion unique).
Usage: python convert_perplexity_thread.py export.md --userid "votre-user-id"
"""

import argparse
import json
import os
import re
import time
import uuid
from typing import Any, Dict, List

# Modèle par défaut pour l'affichage dans OpenWebUI
MODEL = "perplexity"
MODEL_NAME = "perplexity/sonar"
SUBDIR = "perplexity"

def sanitize_text(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    # Supprime les caractères de contrôle privés
    text = re.sub(r'[\ue000-\uf8ff]', '', text)
    return text.strip()

def extract_last_sentence(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    matches = re.findall(r'[^.!?]*[.!?]', cleaned, flags=re.DOTALL)
    if matches:
        return matches[-1].strip()
    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    return lines[-1] if lines else cleaned

def parse_perplexity_markdown(content: str) -> List[Dict[str, Any]]:
    """Parse toutes les conversations du markdown."""
    conversations = []
    # Séparation par la ligne horizontale
    raw_conversations = re.split(r'\n---\n', content)

    for conv_text in raw_conversations:
        if not conv_text.strip():
            continue

        # Le titre est la première ligne commençant par #
        title_match = re.search(r'^#\s+(.+?)$', conv_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"

        if title_match:
            conv_text = conv_text[title_match.end():].strip()

        # Nettoyage de la réponse Perplexity
        response = conv_text
        # Supprime les références de pied de page [^1_1]: url...
        response = re.sub(r'\[?\^\d+_\d+\]:.*?$', '', response, flags=re.MULTILINE)
        # Supprime les marqueurs de citation [^1_1]
        response = re.sub(r'\[\^\d+_\d+\]', '', response)
        # Supprime les spans cachés et logos
        response = re.sub(r'<span style="display:none">.*?</span>', '', response, flags=re.DOTALL)
        response = re.sub(r'<div align="center">.*?</div>', '', response, flags=re.DOTALL)
        response = re.sub(r'<img.*?>', '', response)
        # Normalise les sauts de ligne
        response = re.sub(r'\n{3,}', '\n\n', response).strip()

        conversations.append({
            "user_query": title,
            "assistant_response": response
        })

    return conversations

def build_thread_webui(conversations: List[Dict[str, Any]], user_id: str, filename: str) -> Dict[str, Any]:
    """Construit un fil de discussion unique avec toutes les conversations."""
    conv_uuid = str(uuid.uuid4())
    messages_map = {}
    messages_list = []
    prev_id = None

    # Titre basé sur la première question
    main_title = conversations[0]["user_query"] if conversations else "Perplexity Import"

    # Timestamp de base
    base_timestamp = time.time()

    for idx, conv in enumerate(conversations):
        # Incrémenter légèrement le timestamp pour chaque paire de messages
        current_ts = int(base_timestamp + idx * 2)

        # Message Utilisateur
        user_msg_id = str(uuid.uuid4())
        user_content = sanitize_text(conv["user_query"])

        user_msg = {
            "id": user_msg_id,
            "parentId": prev_id,
            "childrenIds": [],
            "role": "user",
            "content": user_content,
            "timestamp": current_ts,
            "models": [MODEL]
        }

        if prev_id:
            messages_map[prev_id]["childrenIds"].append(user_msg_id)

        messages_map[user_msg_id] = user_msg
        messages_list.append(user_msg)
        prev_id = user_msg_id

        # Message Assistant (si réponse existe)
        if conv["assistant_response"]:
            assistant_msg_id = str(uuid.uuid4())
            assistant_content = sanitize_text(conv["assistant_response"])

            assistant_msg = {
                "id": assistant_msg_id,
                "parentId": prev_id,
                "childrenIds": [],
                "role": "assistant",
                "content": assistant_content,
                "timestamp": current_ts + 1,
                "model": MODEL,
                "modelName": MODEL_NAME,
                "modelIdx": 0,
                "userContext": None,
                "lastSentence": extract_last_sentence(assistant_content),
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "done": True,
            }

            if prev_id:
                messages_map[prev_id]["childrenIds"].append(assistant_msg_id)

            messages_map[assistant_msg_id] = assistant_msg
            messages_list.append(assistant_msg)
            prev_id = assistant_msg_id

    # Structure OpenWebUI
    webui = {
        "id": conv_uuid,
        "title": main_title,
        "models": [MODEL],
        "params": {},
        "history": {
            "messages": messages_map,
            "currentId": prev_id
        },
        "messages": messages_list,
        "tags": [],
        "timestamp": int(base_timestamp * 1000),
        "files": [],
    }

    if user_id:
        webui["userId"] = user_id

    return webui

def slugify(text: str) -> str:
    """Crée un nom de fichier sécurisé."""
    text = re.sub(r'\s+', '_', text.strip())
    text = re.sub(r'[^a-zA-Z0-9_\-]', '', text)
    return text[:50] or "chat"

def run_cli():
    parser = argparse.ArgumentParser(description="Convert Perplexity MD to OpenWebUI JSON (thread)")
    parser.add_argument("files", nargs="+", help="Fichiers Markdown exportés")
    parser.add_argument("--userid", required=True, help="Votre User ID OpenWebUI")
    parser.add_argument("--output-dir", default="output", help="Dossier de sortie")

    args = parser.parse_args()
    outdir = os.path.join(args.output_dir, SUBDIR)
    os.makedirs(outdir, exist_ok=True)

    for path in args.files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            convs = parse_perplexity_markdown(content)
            print(f"Fichier: {path} - {len(convs)} conversation(s) trouvée(s)")

            if not convs:
                print(f"  Aucune conversation à exporter.")
                continue

            # Créer un seul fil de discussion avec toutes les conversations
            webui_obj = build_thread_webui(convs, args.userid, path)

            # Format liste pour OpenWebUI
            final_output = [webui_obj]

            # Nom de fichier basé sur le fichier source
            base_name = os.path.splitext(os.path.basename(path))[0]
            fname = f"{slugify(base_name)}_{webui_obj['id']}.json"

            output_path = os.path.join(outdir, fname)
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump(final_output, fh, ensure_ascii=False, indent=2)

            print(f"  -> Généré : {fname}")
            print(f"     Titre: {webui_obj['title']}")
            print(f"     Messages: {len(webui_obj['messages'])}")

        except Exception as e:
            print(f"Erreur sur {path}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_cli()
