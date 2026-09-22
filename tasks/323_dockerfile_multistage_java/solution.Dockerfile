FROM maven:3.9-eclipse-temurin-{java} AS build
WORKDIR /build
COPY pom.xml .
RUN mvn -B dependency:go-offline
COPY src ./src
RUN mvn -B package -DskipTests

FROM eclipse-temurin:{java}-jre
WORKDIR /app
COPY --from=build /build/target/orders-1.0.0.jar app.jar
ENV PORT={port}
EXPOSE {port}
ENTRYPOINT ["java", "-jar", "app.jar"]
