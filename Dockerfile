FROM python:3.10-alpine
# Python Buffer settings ensure errors are sent to the terminal container
ENV PYTHONUNBUFFERED=1
# Dependencies to get postgres & make working on alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev make libc-dev libffi-dev git libpq
WORKDIR /repo_automator
COPY requirements.txt requirements.txt
COPY .env.example .env
RUN addgroup -S app && adduser -S app -G app
ENV APP_HOME=/repo_automator
# RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
# WORKDIR $APP_HOME
RUN pip3 install -r requirements.txt
COPY entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh
RUN chown -R app:app $APP_HOME
USER app
ENTRYPOINT ["sh","entrypoint.sh"]
