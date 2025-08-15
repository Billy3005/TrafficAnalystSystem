import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.main import bp
from app import db
from app.models import Video

def allowed_file(filename):
    #checkout format of file YES or No
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/', methods=['GET', 'POST'])
def index():
    #route of homepage
    #analyst for update videos
    #show videos had analysted

    if request.method == 'POST':
        #import tasks celery inside finction to avoid circular import
        from tasks.video_tasks import process_video_task

        # check file
        if 'file' not in request.files:
            flash('Không có phần file nào được gửi lên.', 'danger'); return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Chưa có file nào được chọn.', 'warning'); return redirect(request.url)

        # step 1 take time and indetify time from form    
        start_time_str = request.form.get('start_time')
        if not start_time_str:
            flash('Vui lòng chọn thời gian bắt đầu thực tế cho video.', 'danger')
            return redirect(request.url)
        
        try:
            # transform supply to object datetime
            real_start_time = datetime.fromisoformat(start_time_str)
        except ValueError:
            flash('Định dạng thời gian không hợp lệ.', 'danger')
            return redirect(request.url)

        # analyst file
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            random_filename = str(uuid.uuid4()) + '.' + ext
            
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], random_filename))

            #step 2 save real_star_time in database when creating new video
            new_video = Video(
                original_filename=original_filename, 
                saved_filename=random_filename,
                real_start_time=real_start_time 
            )
            db.session.add(new_video); db.session.commit()
            
            # send task background analyst
            task = process_video_task.delay(new_video.id)
            new_video.celery_task_id = task.id
            db.session.commit()
            
            flash(f'Video "{original_filename}" đã được tải lên và đưa vào hàng đợi xử lý!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Định dạng file không được hỗ trợ!', 'danger'); return redirect(request.url)

    # take list videos to show up(method GET)
    videos = Video.query.order_by(Video.upload_timestamp.desc()).all()
    return render_template('index.html', title='Trang chủ', videos=videos)

@bp.route('/dashboard/<int:video_id>')
def dashboard(video_id):
    """
    Route để hiển thị trang dashboard.
    """
    video = Video.query.get_or_404(video_id)
    
    streamlit_url_base = current_app.config['STREAMLIT_URL']
    streamlit_embed_url = f"{streamlit_url_base}?video_id={video.id}"
    
    return render_template(
        'dashboard.html', 
        title=f'Phân tích: {video.original_filename}', 
        video=video,
        streamlit_embed_url=streamlit_embed_url
    )