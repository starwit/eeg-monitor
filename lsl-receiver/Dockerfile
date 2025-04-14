FROM python:3.13-bookworm

ADD https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-bionic_amd64.deb /opt
RUN dpkg -i /opt/liblsl-1.16.2-bionic_amd64.deb

ARG POETRY_VERSION=2.1.2
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /code
# Copy only files that are necessary to install dependencies
COPY poetry.lock poetry.toml pyproject.toml ./
RUN poetry install

COPY ./main.py .

ENTRYPOINT [ "poetry", "run", "python", "main.py" ]