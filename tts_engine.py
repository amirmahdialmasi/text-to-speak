
from pathlib import Path
import edge_tts


async def synthesize_text(
    text: str,
    voice: str,
    output_file: str,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
):
    """
    Convert text to speech and save it as an MP3 file.
    """

    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first to avoid incomplete output.
    temporary = target.with_name(
        f"{target.stem}.partial{target.suffix}"
    )

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )

        await communicate.save(str(temporary))

        if not temporary.exists() or temporary.stat().st_size == 0:
            raise RuntimeError("No audio file was generated.")

        # Replace the destination only after successful generation.
        temporary.replace(target)

    except Exception:
        temporary.unlink(missing_ok=True)
        raise
