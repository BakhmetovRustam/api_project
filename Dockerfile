FROM python:3.10
WORKDIR /app 
COPY  main.py /app/  
RUN apt update
RUN apt install python3-distutils
RUN pip3 install fastapi uvicorn prometheus-client
EXPOSE 8080  
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]