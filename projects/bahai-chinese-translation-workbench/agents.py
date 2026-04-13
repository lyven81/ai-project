import json
import os
import re

import anthropic

MODEL = "claude-sonnet-4-6"


def _get_client():
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_glossary(path="glossary.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_glossary_for_prompt(glossary):
    lines = []
    for term in glossary:
        line = f'- "{term["english"]}" \u2192 "{term["chinese"]}"'
        if term.get("notes"):
            line += f"  ({term['notes']})"
        lines.append(line)
    return "\n".join(lines)


def _strip_markdown_fences(text):
    """Remove ```json ... ``` markdown code fences from LLM output."""
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip())
    return cleaned


def _unwrap_text(raw, target_keys=None):
    """Recursively unwrap JSON/markdown until plain text is found.
    target_keys: list of JSON keys to extract (e.g. ['translation', 'edited_text', 'typeset_text'])
    """
    if target_keys is None:
        target_keys = ["translation", "edited_text", "typeset_text"]
    text = raw
    for _ in range(5):
        text = _strip_markdown_fences(text)
        if text.strip().startswith("{"):
            try:
                data = json.loads(text)
                extracted = None
                for k in target_keys:
                    if k in data and isinstance(data[k], str):
                        extracted = data[k]
                        break
                if extracted:
                    text = extracted
                    continue
                else:
                    break
            except (json.JSONDecodeError, TypeError):
                break
        else:
            break
    return text


def _parse_json_response(text):
    cleaned = _strip_markdown_fences(text)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            # Clean each string value that might contain nested JSON/markdown
            for key in list(parsed.keys()):
                if isinstance(parsed[key], str) and (parsed[key].strip().startswith("```") or parsed[key].strip().startswith("{")):
                    parsed[key] = _unwrap_text(parsed[key])
            return parsed
        except json.JSONDecodeError:
            pass
    return None


TRANSLATION_SYSTEM_PROMPT = """You are translating Baha'i Sacred Writings into Chinese (简体中文).

Three standards govern your translation:
1. ACCURACY (准确): Faithful to the original meaning. Never add, omit, or reinterpret.
2. BEAUTY (文风优美): Elevated, literary Chinese register. Not colloquial. The language must carry the weight and dignity of sacred scripture. Follow the poetic, classical-influenced modern Chinese style — not contemporary casual language.
3. CONSISTENCY (风格一致): Consistent with the translation style established by Shoghi Effendi (the Guardian). Use formal, classical-influenced modern Chinese. Use Chinese punctuation marks (，。；：！？""''《》).

TERMINOLOGY GLOSSARY — You MUST use these approved translations for the following terms:
{glossary_block}

RULES:
- Translate the complete text. Do not summarize or skip any passage.
- Preserve paragraph structure from the source.
- For terms in the glossary, use the approved Chinese translation exactly.
- For proper nouns not in the glossary, transliterate and add the original in parentheses on first occurrence.
- Do not add explanatory notes or commentary within the translation itself.

Return your output as JSON with these keys:
- "translation": the complete Chinese translation (string)
- "term_usage": list of glossary terms you applied, each as {{"english": "...", "chinese": "..."}}
- "notes": any translator notes on difficult passages or choices made (string)

Return ONLY the JSON object, no other text."""


def translation_agent(source_text, source_lang, glossary):
    """Stage 1: Generate Chinese translation draft from source text."""
    client = _get_client()
    glossary_block = format_glossary_for_prompt(glossary)
    system_prompt = TRANSLATION_SYSTEM_PROMPT.replace("{glossary_block}", glossary_block)

    lang_label = {"en": "English", "ar": "Arabic", "fa": "Persian"}.get(source_lang, "English")

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0.3,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Translate the following {lang_label} text into Chinese:\n\n{source_text}"}],
    )

    response_text = response.content[0].text
    prompt_record = f"[System]\n{system_prompt}\n\n[User]\nTranslate the following {lang_label} text into Chinese:\n\n{source_text}"

    parsed = _parse_json_response(response_text)
    if parsed and "translation" in parsed:
        result = {"translation": parsed["translation"], "term_usage": parsed.get("term_usage", []), "notes": parsed.get("notes", "")}
    else:
        result = {"translation": response_text, "term_usage": [], "notes": "Warning: Could not parse structured response. Raw output used."}

    result["prompt_used"] = prompt_record
    result["model_used"] = MODEL
    return result


EDITING_SYSTEM_PROMPT = """You are a Chinese language editor for Baha'i Sacred Writings translation.

You will receive:
1. The original source text
2. A human-approved Chinese translation (from Stage 2 review)

Your task: Refine the translation for grammar, punctuation, tone, and terminology uniformity. Do NOT change the meaning — the human reviewer has already approved the meaning.

Three-standard checklist — evaluate and improve against each:
1. ACCURACY (准确): Does the translation faithfully convey the original? Flag any drift you notice but do not alter meaning.
2. BEAUTY (文风优美): Is the Chinese elevated and literary? Fix colloquial phrasing. Improve rhythm and flow. Ensure the language carries the weight of sacred scripture.
3. CONSISTENCY (风格一致): Are terms used uniformly throughout? Check against the glossary below. Ensure Chinese punctuation is used consistently.

TERMINOLOGY GLOSSARY:
{glossary_block}

RULES:
- Make minimal necessary changes. Respect the human reviewer's approved meaning.
- Fix punctuation: use Chinese punctuation marks (，。；：！？""''《》).
- Ensure paragraph structure matches the source.
- Do not add or remove content.
- For each change you make, provide a brief rationale.

Return your output as JSON with these keys:
- "edited_text": the refined Chinese translation (string)
- "changes_made": list of changes, each as a string describing what was changed and why
- "checklist": object with keys "accuracy", "beauty", "consistency", each containing a brief assessment note (string)

Return ONLY the JSON object, no other text."""


def editing_agent(source_text, approved_translation, glossary):
    """Stage 3: Refine grammar, punctuation, tone, terminology uniformity."""
    client = _get_client()
    glossary_block = format_glossary_for_prompt(glossary)
    system_prompt = EDITING_SYSTEM_PROMPT.replace("{glossary_block}", glossary_block)

    user_message = f"""ORIGINAL SOURCE TEXT:
{source_text}

HUMAN-APPROVED CHINESE TRANSLATION:
{approved_translation}"""

    response = client.messages.create(
        model=MODEL, max_tokens=4096, temperature=0.2, system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = response.content[0].text
    prompt_record = f"[System]\n{system_prompt}\n\n[User]\n{user_message}"

    parsed = _parse_json_response(response_text)
    if parsed and "edited_text" in parsed:
        result = {"edited_text": parsed["edited_text"], "changes_made": parsed.get("changes_made", []), "checklist": parsed.get("checklist", {"accuracy": "", "beauty": "", "consistency": ""})}
    else:
        result = {"edited_text": response_text, "changes_made": ["Warning: Could not parse structured response. Raw output used."], "checklist": {"accuracy": "N/A", "beauty": "N/A", "consistency": "N/A"}}

    result["prompt_used"] = prompt_record
    result["model_used"] = MODEL
    return result
