'''
module : mfileserve.py
Language : Python 3.x
email : andrew@openmarmot.com
github : https://github.com/openmarmot/mfileserve
notes : simple flask http file server. meant for internal networks
'''


from flask import Flask, request, render_template, send_from_directory, redirect
import os
import requests
import threading
import time

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
DOWNLOAD_PREFIX = "downloading_"
TIMEOUT_SECONDS = 7200 # time out of two hours
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    all_files = os.listdir(DOWNLOAD_FOLDER)
    completed_files = [f for f in all_files if not f.startswith(DOWNLOAD_PREFIX)]
    downloading_files = [f for f in all_files if f.startswith(DOWNLOAD_PREFIX)]

    return render_template('index.html', completed_files=completed_files, downloading_files=downloading_files)

def start_download(url):
    if url:
        filename = url.split('/')[-1]
        temp_filepath = os.path.join(DOWNLOAD_FOLDER, DOWNLOAD_PREFIX + filename)
        final_filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(final_filepath):
            print(f"File already exists: {filename}")
            return
        try:
            r = requests.get(url, stream=True,timeout=TIMEOUT_SECONDS)
            with open(temp_filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            os.rename(temp_filepath, final_filepath)
        except requests.Timeout:
            print(f"Download timed out for URL: {url}")
        except Exception as e:
            print(f"An error occurred during download: {e}")
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

@app.route('/download', methods=['POST'])
def download_file():
    url = request.form['url']
    if url:
        download_thread = threading.Thread(target=start_download, args=(url,))
        download_thread.start()
        time.sleep(1) # need to give the download time to start so it shows up on the refresh
    return redirect('/')

@app.route('/files/<filename>')
def files(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
