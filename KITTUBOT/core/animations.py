# Copyright (c) 2026 Naman-devio
# Licensed under the MIT License.
# This file is part of KittuBot

"""
🐾 KITTUBOT Cinematic Animation & Effects Engine
Built for high-concurrency PTB v22 with top-positioned video and aesthetic typography.
"""

import asyncio
import random
from telegram import Update, ReactionTypeEmoji, LinkPreviewOptions
from telegram.ext import ContextTypes
from KITTUBOT.config import config
from KITTUBOT.core.keyboards import get_main_menu_keyboard
from KITTUBOT.core.fonts import to_small_caps
from KITTUBOT import log


async def play_start_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes the signature multi-stage start animation."""
    message = update.effective_message
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Stage 1: Big animated Unicorn 🦄 reaction
    try:
        await message.set_reaction(ReactionTypeEmoji("🦄"), is_big=True)
    except Exception as e:
        log.debug(f"Reaction ignored (chat restriction/private): {e}")

    # Stage 2: Cinematic frame-by-frame intro (Telegram text has no native slide transition,
    # so quick message edits create a lightweight animated/loading effect).
    loader = None
    try:
        frames = [
            "╭━━━〔 🐾 ᴋɪᴛᴛᴜ ᴇɴɢɪɴᴇ 〕━━━╮\n│  ▰▱▱▱▱▱▱▱  ᴡᴀᴋɪɴɢ ᴜᴘ...\n╰━━━━━━━━━━━━━━━━━━━━╯",
            "╭━━━〔 ⚡ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ 〕━━━╮\n│  ▰▰▰▰▱▱▱▱  ʟᴏᴀᴅɪɴɢ ᴍᴏᴅᴜʟᴇs\n╰━━━━━━━━━━━━━━━━━━━━╯",
            "╭━━━〔 ✨ ᴀʟᴍᴏsᴛ ʀᴇᴀᴅʏ 〕━━━╮\n│  ▰▰▰▰▰▰▰▱  ᴘʀᴇᴘᴀʀɪɴɢ ʏᴏᴜʀ ʜᴜʙ\n╰━━━━━━━━━━━━━━━━━━━━╯",
            "╭━━━〔 💜 ᴡᴇʟᴄᴏᴍᴇ 〕━━━╮\n│  ▰▰▰▰▰▰▰▰  ᴀᴄᴄᴇss ɢʀᴀɴᴛᴇᴅ\n╰━━━━━━━━━━━━━━━━━━━━╯",
        ]
        loader = await message.reply_text(frames[0])
        for frame in frames[1:]:
            await asyncio.sleep(0.35)
            await loader.edit_text(frame)
        await asyncio.sleep(0.25)
        await loader.delete()
    except Exception as e:
        log.debug(f"Frame animation step: {e}")
        if loader:
            try:
                await loader.delete()
            except Exception:
                pass

    # Stage 3: Welcome sticker burst
    if config.START_STICKER_FILE_ID:
        try:
            await context.bot.send_sticker(chat_id=chat_id, sticker=config.START_STICKER_FILE_ID)
            await asyncio.sleep(0.2)
        except Exception as e:
            log.debug(f"Sticker send fallback: {e}")

    # Stage 4: Cinematic greeting with Video on Top (show_above_text=True)
    bot_info = await context.bot.get_me()
    random_media = random.choice(config.START_IMG_URL) if config.START_IMG_URL else ""

    bot_title = to_small_caps(config.BOT_NAME)
    text = (
        f'<a href="{random_media}">&#8203;</a>'
        f"╭━━━〔 💜 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {bot_title}</b> 〕━━━╮\n\n"
        f"  ✦ ʜᴇʏ, {user.mention_html()}! ✦\n"
        f"  ʏᴏᴜʀ ɴᴇxᴛ ғᴀᴠᴏᴜʀɪᴛᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ɪs ʜᴇʀᴇ.\n\n"
        f"<blockquote>🎮 <b>ɢᴀᴍᴇs</b>  •  💰 <b>ᴇᴄᴏɴᴏᴍʏ</b>\n"
        f"🛡️ <b>ɢʀᴏᴜᴘ ᴛᴏᴏʟs</b>  •  ✨ <b>ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ</b>\n\n"
        f"ᴇxᴘʟᴏʀᴇ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ ᴀɴᴅ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴄʜᴀᴛ ᴍᴏʀᴇ ғᴜɴ.</blockquote>\n"
        f"╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"⚡ <b>sᴛᴀᴛᴜs:</b> <code>ᴏɴʟɪɴᴇ & ʀᴇᴀᴅʏ</code>\n"
        f"👇 <b>ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ.</b>"
    )

    kwargs = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": get_main_menu_keyboard(bot_info.username),
    }

    # Place video on the UPPER side of the caption
    if random_media:
        kwargs["link_preview_options"] = LinkPreviewOptions(
            url=random_media,
            is_disabled=False,
            prefer_large_media=True,
            show_above_text=True,  # Video appears ABOVE the caption!
        )

    if config.MESSAGE_EFFECT_ID:
        kwargs["message_effect_id"] = config.MESSAGE_EFFECT_ID

    try:
        await context.bot.send_message(**kwargs)
    except Exception as e:
        log.warning(f"Failed with message_effect_id, falling back: {e}")
        kwargs.pop("message_effect_id", None)
        await context.bot.send_message(**kwargs)
