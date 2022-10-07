import requests
from api_secrets import API_KEY_ASSEMBLYAI
import sys # to input file name from the terminal
import time # to add delay between two consecutive polls


upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcribe_endpoint = "https://api.assemblyai.com/v2/transcript"
audio_file = sys.argv[1] # input audio file from system. Run syntax: py main.py audio_filename
headers = {'authorization': API_KEY_ASSEMBLYAI}


# Upload File
def upload(audio_file):
    def read_file(audio_file, chunk_size=5242880):
        with open(audio_file, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(audio_file))

    audio_url = upload_response.json()['upload_url']
    return audio_url


# Transcribe
def transcribe(audio_url):
    transcript_request = { "audio_url": audio_url }
    transcipt_response = requests.post(transcribe_endpoint, json=transcript_request, headers=headers)
    # print(transcipt_response.json())
    job_id = transcipt_response.json()['id'] # used in polling, to check whether AssemblyAI has completed the transcription
    return job_id


# Poll - Check if the transcription is over

def poll(transcript_id):
    polling_endpoint = transcribe_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers) # Getting information from Assembly AI
    # print(polling_response.json())
    # print(transcript_id)
    # print(polling_response)
    return polling_response.json()


def get_transcription_result_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
        print('Waiting for 30 seconds...')
        time.sleep(30)
            

# Save the generated transcript

# def save_transcript(audio_url):
#     data, error = get_transcription_result_url(audio_url)

#     if data:
#         print(data['text'])
#         print('Confidence', data['confidence'])
#         text_file = audio_file + '.txt'
#         with open(text_file, "w") as f:
#             f.write(data['text'])
#         print('Transcription Saved Successfully')

#     elif error:
#         print("An Error Occured", error)


audio_url = upload(audio_file)
from langdetect import detect
def langResult(audio_url):
    data, error = get_transcription_result_url(audio_url)

    if data:
        print(data['text'])
        print('Confidence', data['confidence'])
        print(detect(data['text']))

# audio_url = upload(audio_file)
langResult(audio_url)
# save_transcript(audio_url)
