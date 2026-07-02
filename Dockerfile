FROM 

RUN apk update && apk install ffmpeg

RUN uv pip install -r requirements.txt