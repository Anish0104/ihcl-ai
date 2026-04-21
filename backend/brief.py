import os

from groq import Groq

from prompts import BRIEF_SYSTEM_PROMPTS


def generate_brief(guest_data: dict, property_name: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    guest_info = f"""
Guest Name: {guest_data.get('name', 'Not provided')}
Occasion/Purpose: {guest_data.get('occasion', 'Not specified')}
Arrival: {guest_data.get('arrival', 'Not specified')}
Departure: {guest_data.get('departure', 'Not specified')}
Accommodation Type: {guest_data.get('room_type', 'Not specified')}
Number of Guests: {guest_data.get('num_guests', 'Not specified')}
Dietary Restrictions/Allergies: {guest_data.get('dietary', 'None noted')}
Known Preferences: {guest_data.get('preferences', 'None on file')}
Past Stay Notes: {guest_data.get('past_stays', 'No previous stay history — NOTE: production version would pull full history from PMS/CRM')}
Special Requests: {guest_data.get('special_requests', 'None')}
Additional Notes: {guest_data.get('notes', 'None')}
""".strip()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        stream=False,
        messages=[
            {"role": "system", "content": BRIEF_SYSTEM_PROMPTS[property_name]},
            {
                "role": "user",
                "content": (
                    "Generate a complete pre-arrival brief for the following guest:\n"
                    f"{guest_info}"
                ),
            },
        ],
    )

    return response.choices[0].message.content
