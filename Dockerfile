FROM continuumio/miniconda3

MAINTAINER Sean Rose "seanrose949@gmail.com"

# Create working directory
WORKDIR /app

# Update conda
RUN conda update -n base -c defaults conda

# Copy conda environment
COPY environment.yml .

# Create environment
RUN conda env create -n py37base -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "py37base", "/bin/bash", "-c"]

# Make sure the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Copy over code and run
COPY app.py .
COPY helper_functions.py .
COPY assets ./assets
ENTRYPOINT ["conda", "run", "-n", "py37base", "python", "app.py"]
