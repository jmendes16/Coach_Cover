# docker run will need the -i flag and the -v bind mount flag (more details in UserInteractions.py)
FROM python:3.12.1

ADD main.py .
ADD iCalMod.py .
ADD UserInteractions.py .

RUN pip install datetime icalendar pandas

CMD [ "python", "./main.py" ]