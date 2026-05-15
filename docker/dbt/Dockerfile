# Use a base Python image
FROM python:3.10-slim

# Install dbt and dbt-postgres
RUN pip install dbt-core dbt-postgres

# Working directory inside the container
WORKDIR /src/dbt_project

# Copy profiles.yml into dbt's default profiles location
COPY dbt_project/profiles.yml /root/.dbt/profiles.yml

# Copy the dbt project files into the container
COPY ./dbt_project .

# Build all models on container start; keep the container alive after with `tail -f`
CMD ["bash", "-c", "\
    echo '🚀 Running dbt build...'; \
    dbt clean; \
    dbt deps --profiles-dir /root/.dbt; \
    dbt debug --profiles-dir /root/.dbt; \
    dbt build --profiles-dir /root/.dbt; \
    echo '✅ dbt build complete.'; \
    tail -f /dev/null \
"]
