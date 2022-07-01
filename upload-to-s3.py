import requests
import boto3
from secrets import access_key, secret_key, zoom_access_token

import urllib3
import certifi


def get_meeting_recording(meeting_id, bearer_token, file_type):
    """
    Get the recording for a meeting
    """
    bearer_token = 'Bearer' + bearer_token
    api_url = 'https://api.zoom.us/v2/meetings/'+ meeting_id +'/recordings'
    headers = {
    'Authorization': bearer_token,
    }
    
    try:
        response = requests.request("GET", api_url, headers=headers)
        
        if response.status_code == 200:
            recording_files= response.json()['recording_files']
            
            for recording_file in recording_files:
                if recording_file['file_type'] and file_type == 'MP4':
                    return recording_file['download_url']
                elif recording_file['file_type'] and file_type == 'MPA':
                    return recording_file['download_url']
                elif recording_file['file_type'] and file_type ==  'TIMELINE':
                    return recording_file['download_url']
                else: 
                    return print("No recording found")
    except Exception as e:
        print("Exception was rasied" + str(e))
        return None

def upload_recording_to_s3(download_url, bucket, upload_download_key):
    """
    Upload the recording to S3
    """
    download_url =  download_url
    new_download_url =  download_url +'?access_token=' + zoom_access_token
    http=urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())

    try:
        get_recording = http.request('GET', new_download_url,preload_content=False)
        if get_recording.status == 200:
            s3=boto3.client('s3',aws_access_key_id=access_key, aws_secret_access_key=secret_key)

            """
            The upload_fileobj method is provided by the S3 Client, Bucket, and Object classes. 
            It accepts a readable file-like object. The file object must be opened in binary mode,
            not text mode.
            """
            s3.upload_fileobj(get_recording, bucket , upload_download_key)
    except Exception as e:
        print("Exception was rasied" + str(e))
        return None
    return True
    
meeting_id = "91842375871" #meeting number of the recording you want to download
bearer_token = zoom_access_token # zoom_access_token
file_type = 'MP4' # MP4, MPA, TIMELINE

s3_bucket = 'tstbucket00' #your s3 bucket
s3_path_filename = 'rec/folder.mp4' #your desired s3 path or filename


rec_download_url = get_meeting_recording( meeting_id ,bearer_token, file_type)
upload_recording_to_s3(rec_download_url, s3_bucket, s3_path_filename)







