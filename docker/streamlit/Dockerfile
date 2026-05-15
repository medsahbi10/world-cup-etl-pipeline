# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install libraries
RUN pip install pandas streamlit plotly SQLAlchemy python-dotenv psycopg2-binary

# Copy streamlit code into the container
COPY ./streamlit .

EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
