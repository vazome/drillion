FROM golang:{go} AS build
WORKDIR /src
COPY go.mod ./
COPY main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/{name} .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/{name} /{name}
EXPOSE 8080
ENTRYPOINT ["/{name}"]
