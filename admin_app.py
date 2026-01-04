import os
import threading
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from database import load_pdf_to_vector_store, load_website_to_vector_store, COMPANY_WEBSITE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_purposes'  
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'md'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_ingestion_background():
    """Runs data ingestion in a background thread."""
    logger.info("Starting background data ingestion...")
    try:
        load_pdf_to_vector_store(UPLOAD_FOLDER)
        logger.info("Background data ingestion completed.")
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")

def run_hardcoded_web_ingestion():
    """Starts ingestion for the hardcoded company URL."""
    if COMPANY_WEBSITE_URL:
        logger.info(f"Starting background web ingestion for hardcoded URL: {COMPANY_WEBSITE_URL}")
        try:
            load_website_to_vector_store(COMPANY_WEBSITE_URL, max_depth=2)
            logger.info(f"Background web ingestion for {COMPANY_WEBSITE_URL} completed.")
        except Exception as e:
            logger.error(f"Hardcoded web ingestion failed: {e}")
    else:
        logger.info("No COMPANY_WEBSITE_URL defined, skipping web ingestion.")


@app.route('/')
def index():
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('file')
    
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    saved_count = 0
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            saved_count += 1
            
    if saved_count > 0:
        flash(f'{saved_count} file(s) uploaded successfully. Ingestion started in background.')
        # Trigger ingestion in background
        thread = threading.Thread(target=run_ingestion_background)
        thread.daemon = True
        thread.start()
    else:
        flash('No valid files were uploaded (check allowed extensions)')
        
    return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not allowed_file(filename): 
         flash('Invalid filename')
         return redirect(url_for('index'))
         
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'{filename} deleted successfully')
            thread = threading.Thread(target=run_ingestion_background)
            thread.daemon = True
            thread.start()

        except Exception as e:
            flash(f'Error deleting file: {e}')
    else:
        flash('File not found')
        
    return redirect(url_for('index'))

def start_background_ingestion_on_boot():
    logger.info("Triggering initial data ingestion on startup...")
    # PDF Ingestion
    pdf_thread = threading.Thread(target=run_ingestion_background)
    pdf_thread.daemon = True
    pdf_thread.start()
    
    # Web Ingestion
    web_thread = threading.Thread(target=run_hardcoded_web_ingestion)
    web_thread.daemon = True
    web_thread.start()

if __name__ == '__main__':
    print(f"Starting Flask Admin Dashboard...")
    print(f"Monitoring folder: {UPLOAD_FOLDER}")
    # Start ingestion on launch
    start_background_ingestion_on_boot()
    app.run(debug=True, port=5000)
