from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto, Message


async def send_photos(bot: Bot, s3Paths: list[str], text: str, user_id: int):
    if len(s3Paths) == 1:
        try:
            original_photo = FSInputFile(s3Paths[0])
            await bot.send_photo(user_id, photo=original_photo, caption=text)
        except Exception as e:
            print(f"Error sending original photo {s3Paths[0]}: {e}")
            # await message.bot.send_message(user_id, "Не удалось загрузить текущее фото.")
    else:
        media = []
        for i, s3path in enumerate(s3Paths):
            try:
                file = FSInputFile(s3path)
                media.append(InputMediaPhoto(media=file, caption= text if i == 0 else None))
            except Exception as e:
                print(f"Error sending original photo {s3path}: {e}")
                # await message.bot.send_message(user_id, "Не удалось загрузить текущее фото.")
        await bot.send_media_group(user_id, media)