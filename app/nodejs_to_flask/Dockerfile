
FROM python:stretch

# Create app directory
COPY . /app
WORKDIR /app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source 

ENTRYPOINT ["python3","app.py"]
