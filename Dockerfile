FROM python:3.10.9

# Working directory
WORKDIR /app

# System info
RUN echo `uname -a`
RUN echo `python --version`

# Install requirements
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN pip install dgl -f https://data.dgl.ai/wheels/repo.html

# Add source code
ADD . /app

# Expose port 80
# This is important in order for the Azure App Service to pick up the app
ENV PORT 80
EXPOSE 80

ENTRYPOINT ["python", "main.py"]
CMD ["web"]
