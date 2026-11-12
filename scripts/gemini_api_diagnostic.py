"""Run a minimal Gemini model-access and text-generation diagnostic."""

import argparse
import getpass
import sys

from google import genai
from google.genai import types


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gemini-3.8-flash")
    args = parser.parse_args()

    api_key = getpass.getpass("Gemini API key (input hidden): ").strip()
    if not api_key:
        print("No API key provided.")
        return 2

    client = genai.Client(api_key=api_key)
    print(f"Checking model access: {args.model}")
    try:
        model = client.models.get(model=args.model)
        print(f"Model access OK: {getattr(model, 'name', args.model)}")
    except Exception as exc:
        print(f"Model access failed: {type(exc).__name__}: {exc}")
        return 1

    print("Sending one short translation request...")
    try:
        response = client.models.generate_content(
            model=args.model,
            contents="Translate 'Good morning' into Vietnamese. Return only the translation.",
            config=types.GenerateContentConfig(max_output_tokens=32),
        )
        result = response.text
        if not result or not result.strip():
            print("Generation returned an empty response.")
            return 1
        print(f"Generation OK: {result.strip()}")
        return 0
    except Exception as exc:
        print(f"Generation failed: {type(exc).__name__}: {exc}")
        if "503" in str(exc) or "UNAVAILABLE" in str(exc).upper():
            print("The model endpoint is currently unavailable/overloaded; retry later or test another model.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
