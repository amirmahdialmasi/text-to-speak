
import asyncio
import edge_tts


def fetch_available_voices():
    """
    دریافت فهرست صداهای موجود از Edge TTS.
    """

    voices = asyncio.run(edge_tts.list_voices())

    if not isinstance(voices, list):
        raise RuntimeError("Invalid voice list received.")

    return voices


def filter_voices(
    voices,
    language="همه زبان‌ها",
    gender="همه",
    search=""
):
    """
    فیلتر صداها بر اساس:
    - زبان
    - جنسیت
    - نام و مشخصات صدا
    """

    results = []

    search = search.strip().casefold()

    for voice in voices:

        name = voice.get("ShortName", "")
        locale = voice.get("Locale", "")
        voice_gender = voice.get("Gender", "")
        friendly_name = voice.get("FriendlyName", "")

        # Language filter
        if language == "فارسی":

            if not locale.lower().startswith("fa-"):
                continue

        elif language == "English":

            if not locale.lower().startswith("en-"):
                continue

        # Gender filter
        if gender != "همه":

            if voice_gender.lower() != gender.lower():
                continue

        # Search filter
        searchable_text = " ".join([
            name,
            locale,
            voice_gender,
            friendly_name,
            str(voice.get("VoiceTag", {}))
        ]).casefold()

        if search and search not in searchable_text:
            continue

        results.append(voice)

    return sorted(
        results,
        key=lambda item: (
            item.get("Locale", ""),
            item.get("ShortName", "")
        )
    )
