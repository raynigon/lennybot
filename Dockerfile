FROM python:3 as build

RUN python -m pip install --upgrade pip && \
    pip install setuptools wheel twine build && \
    mkdir -p /build/
WORKDIR /build/
COPY . .
RUN python3 -m build

FROM python:3

WORKDIR /workspace/
COPY --from=build /build/dist/*.whl .
RUN pip install *.whl && rm *.whl

CMD ["lennybot", "ci"]