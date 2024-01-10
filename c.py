import os
from PIL import Image
import cv2 as cv
import pytesseract
import telebot

# Set up the Telegram bot
bot = telebot.TeleBot("6327046920:AAFwsMtmet-Jz8dN9VEm3LByP13hPFjpDqg")

def detect_subtitles(file):
    # Load the image and resize it for better OCR detection
    img = cv.imread(file)
    resized_img = cv.resize(img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

    # Convert the image to grayscale and apply thresholding for better OCR detection
    img_gray = cv.cvtColor(resized_img, cv.COLOR_BGR2GRAY)
    retval, thresh_image = cv.threshold(img_gray, 100, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)

    # Save the processed image for OCR detection
    processed_file = "processed_" + file
    cv.imwrite(processed_file, thresh_image)

    # Detect subtitles using pytesseract library and return the detected text
    detected_text = pytesseract.image_to_string(Image.open(processed_file), lang="rus")
    os.remove(processed_file)  # Delete the processed image file after OCR detection

    return detected_text

@bot.message_handler(content_types=["video"])
def handle_video(message):
    try:
        chat_id = message.chat.id

        # Download the video and split it into frames (images)
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        video_capture = cv.VideoCapture(downloaded_file)

        current_frame = 0
        subtitles = ""
        while True:
            success, frame = video_capture.read()

            if not success:
                break


            # Process the image for better OCR detection and save it as a temporary file
            processed_image = "processed_" + str(current_frame) + ".jpg"
            cv.imwrite(processed_image, frame)

            # Detect subtitles from each frame (image) using the detect_subtitles function
            detected_text = detect_subtitles(processed_image)

            if detected_text:
                subtitles += detected_text + "\n"  # Add the detected text to the overall subtitles string

            os.remove(processed_image)  # Delete the processed image file after OCR detection

            current_frame += 1

        video_capture.release()

        if not subtitles:
            bot.reply_to(message, "No subtitles detected in this video!")
        else:
            # Send the detected subtitles to the user
            bot.send_document(chat_id, subtitles)

    except Exception as e:
        print("An error occurred while processing the video file:", str(e)) 

bot.polling()
