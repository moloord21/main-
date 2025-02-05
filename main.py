import requests
import asyncio
from telethon import TelegramClient, events, errors, types
import nest_asyncio
import os
import time

# Apply nest_asyncio
nest_asyncio.apply()

# Telegram API credentials
api_id = 27043190
api_hash = '888157bea9d93b1502a86c7ab61e1eca'
bot_token = '7419858376:AAHvZ4BcERR4TXsRrZmvoY1Q3Uma5AFttcI'

# Use a unique session name
SESSION_NAME = f'bot_session_{int(time.time())}'

# Add your channel username here
CHANNEL_USERNAME = '@husr12'  # Replace with your channel username

# قائمة بأسماء السور القرآنية
SURAH_NAMES = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه",
    # ... باقي السور كما هي
]

async def download_and_upload_sura(client, sura_number):
    sura_str = str(sura_number).zfill(3)
    url = f'https://server13.mp3quran.net/husr/{sura_str}.mp3'
    file_name = f'سورة {SURAH_NAMES[sura_number-1]}'
    temp_file = f'temp_{sura_str}.mp3'

    try:
        print(f'📥 جاري تحميل {file_name}...')
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            caption = file_name

            for attempt in range(3):
                try:
                    print(f'📤 جاري رفع {file_name} إلى تيليجرام (المحاولة {attempt + 1})...')

                    # استخدام types.DocumentAttributeAudio بدلاً من events.Raw
                    attributes = [
                        types.DocumentAttributeAudio(
                            duration=0,  # سيتم تحديده تلقائياً
                            title=file_name,
                            performer="محمود خليل الحصري"
                        )
                    ]

                    await client.send_file(
                        CHANNEL_USERNAME,
                        temp_file,
                        caption=caption,
                        attributes=attributes,
                        force_document=False
                    )
                    print(f'✅ تم رفع {file_name} بنجاح')
                    break

                except errors.ChatWriteForbiddenError:
                    print("❌ البوت لا يملك صلاحيات الإرسال!")
                    raise
                except Exception as upload_error:
                    if attempt == 2:
                        raise upload_error
                    print(f"خطأ: {str(upload_error)}")
                    await asyncio.sleep(10)

            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f'🧹 تم حذف الملف المؤقت')

    except Exception as e:
        print(f'❌ حدث خطأ أثناء معالجة {file_name}: {str(e)}')
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise

async def main():
    for file in os.listdir():
        if file.startswith('bot_session_') and file.endswith('.session'):
            try:
                os.remove(file)
            except:
                pass

    try:
        client = TelegramClient(SESSION_NAME, api_id, api_hash)
        await client.start(bot_token=bot_token)
        print("✅ تم تشغيل البوت بنجاح!")

        for sura_number in range(1, 115):
            try:
                await download_and_upload_sura(client, sura_number)
                await asyncio.sleep(5)
            except KeyboardInterrupt:
                print("\n⚠️ تم إيقاف العملية بواسطة المستخدم...")
                break
            except Exception as e:
                print(f"❌ خطأ في {SURAH_NAMES[sura_number-1]}: {str(e)}")
                response = input("هل تريد الاستمرار مع السورة التالية؟ (y/n): ")
                if response.lower() != 'y':
                    break

    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
    finally:
        session_file = f'{SESSION_NAME}.session'
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except:
                pass
        try:
            await client.disconnect()
        except:
            pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف العملية بواسطة المستخدم")
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
