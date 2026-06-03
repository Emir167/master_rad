import os
from typing import Any

from dotenv import load_dotenv


load_dotenv()


def generate_mock_response(user_question: str, routing_result: dict[str, Any] | None = None) -> str:
    selected_mode = "Auto Mode"
    planned_tools = ["SQL Tool", "Document RAG Tool", "Web Tool"]

    if routing_result:
        selected_mode = routing_result.get("selected_mode", selected_mode)
        planned_tools = routing_result.get("planned_tools", planned_tools)

    return f"""
### Mock LLM odgovor

Gemini API key nije pronađen ili Gemini poziv nije uspeo, pa aplikacija trenutno koristi mock režim.

**Pitanje korisnika:**  
{user_question}

**Detektovani režim:**  
{selected_mode}

**Planirani alati:**  
{", ".join(planned_tools)}

### Pretpostavka

U finalnoj verziji sistem bi koristio SQL bazu, interne izveštaje i web kontekst da generiše konkretnu preporuku.

### Preporuka

Za sada je ovo samo testni odgovor. Ako želiš pravi Gemini odgovor, proveri da li postoji `.env` fajl i da li je u njemu ispravno podešen `GEMINI_API_KEY`.
"""


def generate_response(
    user_question: str,
    routing_result: dict[str, Any] | None = None,
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    """
    Generates response using Gemini API.

    If GEMINI_API_KEY is missing or the API call fails,
    the function returns a mock response instead of crashing.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_mock_response(user_question, routing_result)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        selected_mode = "Auto Mode"
        planned_tools = ["SQL Tool", "Document RAG Tool", "Web Tool"]

        if routing_result:
            selected_mode = routing_result.get("selected_mode", selected_mode)
            planned_tools = routing_result.get("planned_tools", planned_tools)

        history_text = ""
        if chat_history:
            recent_messages = chat_history[-6:]
            history_text = "\n".join(
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            )

        prompt = f"""
Ti si AI asistent za master rad na temu:
"MCP multi-agentski sistem za e-commerce analitiku i objašnjive poslovne preporuke".

Sistem će kasnije koristiti:
1. SQL bazu sa prodajnim podacima,
2. interne PDF/Word izveštaje kroz RAG,
3. web informacije o tržištu,
4. recommendation agenta.

Trenutno se testira samo LLM API konekcija.

Korisnikovo pitanje:
{user_question}

Detektovani režim:
{selected_mode}

Planirani alati:
{", ".join(planned_tools)}

Prethodni razgovor:
{history_text}

Odgovori na srpskom jeziku.
Odgovor strukturiraj ovako:
1. Kratko razumevanje pitanja
2. Koji izvori bi se koristili
3. Koje pretpostavke praviš
4. Poslovna preporuka
5. Napomena da je trenutno ovo LLM test, bez stvarne SQL/RAG/MCP analize
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    except Exception as error:
        return f"""
### Mock fallback odgovor

Gemini API key postoji, ali poziv ka Gemini API-ju nije uspeo.

**Greška:**  
`{error}`

**Pitanje korisnika:**  
{user_question}

Aplikacija nije pukla, što znači da fallback sistem radi. Sledeće proveri:
- da li je API key ispravan,
- da li imaš internet,
- da li je instaliran paket `google-genai`,
- da li model `gemini-2.5-flash` imaš dostupan na nalogu.
"""