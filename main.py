from flask import Flask, request, render_template, send_file, redirect, url_for
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import os
import youtube_dl

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    video_url = request.form['video_url']
    video_id = video_url.split("v=")[1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([t['text'] for t in transcript])
        return render_template('index.html', transcript=transcript_text, video_id=video_id)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/download_pdf/<video_id>', methods=['GET'])
def download_pdf(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([t['text'] for t in transcript])
        pdf_filename = create_pdf(transcript_text, video_id)
        return send_file(pdf_filename, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/download_audio/<video_id>', methods=['GET'])
def download_audio(video_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'transcripts/{video_id}.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'verbose': True  # Add verbose flag for detailed output
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        
        audio_file = f'transcripts/{video_id}.mp3'
        return send_file(audio_file, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}"

    try:
        # Using youtube_dl to download audio from YouTube video
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'transcripts/{video_id}.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        
        audio_file = f'transcripts/{video_id}.mp3'
        return send_file(audio_file, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {e}"

def create_pdf(text, video_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    filename = f"transcripts/{video_id}.pdf"
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')
    pdf.output(filename)
    return filename

if __name__ == '__main__':
    app.run(debug=True)
