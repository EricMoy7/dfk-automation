FROM python
ADD . ./dfk-automation
WORKDIR /dfk-automation
RUN pip install -r requirements.txt
CMD ["python", "main.py"]


