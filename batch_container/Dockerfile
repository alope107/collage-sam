FROM redcliffesalaman/collage-model
#TODO(auberon) pin to specific image version?

COPY ./requirements.txt /requirements/requirements.txt
RUN pip install -r /requirements/requirements.txt

COPY ./app /app

ENTRYPOINT ["python", "/app/job_runner.py"]