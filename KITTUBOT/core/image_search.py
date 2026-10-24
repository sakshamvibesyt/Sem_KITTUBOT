
import logging
import random
import re

import httpx

logger = logging.getLogger(__name__)

API_URL = "https://commons.wikimedia.org/w/api.php"

PHOTO_TRIGGERS = re.compile(
    r"\b(?:hot\s+pics?|sexy\s+pics?|glamou?r(?:ous)?\s+pics?|"
    r"cute\s+(?:girl\s+)?pics?|girl\s+photos?|model\s+photos?|"
    r"send\s+selfie|selfie\s+bhejo|apni\s+(?:selfie|photo)|"
    r"photo\s+bhejo|pic\s+bhejo|photos?\s+bhejo|"
    r"send\s+(?:me\s+)?(?:a\s+)?(?:photo|pic|selfie))\b",
    re.IGNORECASE,
)


def get_photo_query(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ("cute", "pretty", "selfie")):
        return "woman portrait fashion"

    if any(word in text for word in ("hot", "sexy", "glamour", "model")):
        return "fashion model portrait"

    return "fashion portrait"


async def send_requested_photo(message, text: str) -> bool:
    """Search Wikimedia Commons and upload a downloaded image to Telegram."""
    if not text or not PHOTO_TRIGGERS.search(text):
        return False

    query = get_photo_query(text)

    headers = {
        "User-Agent": "GunnuKITTUBOT/1.0 (Telegram image search)"
    }

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,
        "gsrlimit": 20,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1000,
    }

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            candidates = []

            for page in pages.values():
                title = page.get("title", "")

                # Skip results whose titles indicate explicit content.
                if re.search(
                    r"\b(nude|nudity|porn|pornographic|explicit|erotic|xxx)\b",
                    title,
                    re.IGNORECASE,
                ):
                    continue

                image_info_list = page.get("imageinfo") or []
                if not image_info_list:
                    continue

                info = image_info_list[0]
                image_url = info.get("thumburl") or info.get("url", "")

                if not image_url.startswith("https://"):
                    continue

                candidates.append(
                    (
                        image_url,
                        info.get("descriptionurl", ""),
                        info.get("extmetadata", {})
                        .get("LicenseShortName", {})
                        .get("value", ""),
                    )
                )

            random.shuffle(candidates)

            # Try multiple images in case one URL fails.
            for image_url, source_url, license_name in candidates[:8]:
                try:
                    image_response = await client.get(image_url)
                    image_response.raise_for_status()

                    content_type = image_response.headers.get(
                        "content-type", ""
                    ).lower()
                    image_bytes = image_response.content

                    if not content_type.startswith("image/"):
                        continue

                    if len(image_bytes) < 1024:
                        continue

                    caption = "😈 Lo ji, photo aa gayi! 💜"

                    if source_url:
                        caption += f"\n📷 Source: {source_url}"

                    if license_name:
                        caption += f"\n📝 License: {license_name}"

                    await message.reply_photo(
                        photo=image_bytes,
                        caption=caption[:1000],
                    )
                    return True

                except Exception:
                    logger.exception(
                        "Could not send candidate image: %s",
                        image_url,
                    )

        await message.reply_text(
            "🥹 Is baar usable photo nahi mili. "
            "Thodi der baad dobara try karo!"
        )
        return True

    except Exception:
        logger.exception(
            "Wikimedia photo search failed for query=%r",
            query,
        )
        await message.reply_text(
            "🥲 Photo search abhi fail ho rahi hai. "
            "Baaki bot chat normal chalni chahiye."
        )
        return True
        
