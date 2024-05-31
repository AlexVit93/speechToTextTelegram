import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import whisper
from pydub import AudioSegment
import tempfile
from config import TOKEN_NUM

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

model = whisper.load_model("base")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне аудиофайл или голосовое сообщение, и я его транскрибирую.')

async def handle_audio(file, update: Update) -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        await file.download_to_drive(tmp_file.name)
        tmp_file.close()
        audio = AudioSegment.from_file(tmp_file.name)
        wav_path = tmp_file.name + '.wav'
        audio.export(wav_path, format='wav')

        result = model.transcribe(wav_path)
        await update.message.reply_text(result["text"])

        os.remove(tmp_file.name)
        os.remove(wav_path)

async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    audio_file = await update.message.audio.get_file()
    await handle_audio(audio_file, update)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice_file = await update.message.voice.get_file()
    await handle_audio(voice_file, update)

def main() -> None:
    TOKEN = TOKEN_NUM
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO, audio_handler))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))

    application.run_polling()

if __name__ == '__main__':
    main()
