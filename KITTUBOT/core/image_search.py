
import httpx
import re
import html

API_URL = "https://commons.wikimedia.org/w/api.php"

PHOTO_TRIGGERS = re.compile(
    r"\b(hot pic|hot photo|sexy pic|sexy photo|"
    r"glamour pic|glamorous photo|cute girl pic|"
    r"girl photo|model photo|send selfie|"
    r"apni selfie|apni photo|photo bhejo|pic bhejo|"
    r"selfie bhejo|hot pics|sexy pics|cute pics)\b",
    re.IGNORECASE,
)

def get_photo_query(text: str):
    text = text.lower()

    if any(word in text for word in ("cute", "pretty", "selfie")):
        return "portrait fashion woman"

    if any(word in text for word in ("hot", "sexy", "glamour", "model")):
        return "glamour fashion model portrait"

    return "fashion portrait woman"


async def send_requested_photo(message, text: str) -> bool:
    if not text or not PHOTO_TRIGGERS.search(text):
        return False

    query = get_photo_query(text)

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 15,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1000,
    }

    headers = {
        "User-Agent": "GunnuKITTUBOT/1.0 (Telegram image search)"
    }

    try:
        async with httpx.AsyncClient(
            timeout=15,
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
            info_list = page.get("imageinfo", [])
            if not info_list:
                continue

            info = info_list[0]
            image_url = info.get("thumburl") or info.get("url", "")

            if not image_url.startswith("https://"):
                continue

            if not image_url.lower().split("?")[0].endswith(
                (".jpg", ".jpeg", ".png", ".webp")
            ):
                continue

            # Avoid obviously unsuitable results.
            if re.search(
                r"\b(nude|nudity|porn|pornographic|"
                r"explicit|erotic|xxx)\b",
                title,
                re.IGNORECASE,
            ):
                continue

            metadata = info.get("extmetadata", {})
            license_name = (
                metadata.get("LicenseShortName", {}).get("value", "")
            )
            description_url = info.get("descriptionurl", "")

            candidates.append(
                (image_url, title, license_name, description_url)
            )

        if not candidates:
            await message.reply_text(
                "🥹 Is baar achhi photo nahi mili, thodi der baad try karo!"
            )
            return True

        import random
        image_url, title, license_name, page_url = random.choice(candidates)

        caption = "😈 Lo ji, tumhari photo aa gayi! 💜"
        if page_url:
            caption += f"\n\n📷 Source: {page_url}"
        if license_name:
            caption += f"\n📝 License: {license_name}"

        await message.reply_photo(
            photo=image_url,
            caption=caption,
        )
        return True

    except Exception:
        await message.reply_text(
            "🥲 Photo search abhi kaam nahi kar raha. Thodi der baad try karo!"
        )
        return True
  
