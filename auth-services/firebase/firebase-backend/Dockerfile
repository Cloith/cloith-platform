# 1. Build Stage
FROM golang:1.22-alpine AS build

# Install build dependencies and Air for live reloading
RUN apk add --no-cache git
RUN go install github.com/air-verse/air@latest

WORKDIR /app

# Leverage Docker cache for dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source code
COPY . .

# Build the binary (though Air will handle this in development)
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# 2. Final Run Stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

# Copy the binary and the Air tool from the build stage
COPY --from=build /app/main .
COPY --from=build /go/bin/air /usr/local/bin/air

# Copy the source code for Air to watch (Crucial for live reload)
COPY . .

# Create the secrets directory (where K8s will mount the volume)
RUN mkdir -p /app/secrets

# The port you chose for Auth
EXPOSE 3000

# Start with Air for development (it will re-compile on file changes)
ENTRYPOINT ["air"]