FROM python:2.7
LABEL maintainer="Isaac Tan"

COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt

# Expose port 3111
EXPOSE 3111

# command to run on container start
CMD [ "python", "init_db.py"]
CMD [ "python", "app.py" ]
