---
title: "a JVM image: build with Maven, run on a JRE"
difficulty: hard
minutes: 20
prereqs: [297]
track: docker
tags: [docker, dockerfile, multi-stage, java, maven, layer-cache]
kind: docker
edits: Dockerfile
---
# a JVM image: build with Maven, run on a JRE

*Maven, the JDK and the local repository come to well over half a gigabyte. The app they build is one jar, and running it needs a JRE and nothing else.*

## Read first
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/): build in one stage, copy the result into another
- [eclipse-temurin](https://hub.docker.com/_/eclipse-temurin): the `-jre` tags, and the `-jdk` ones the build needs
- [dependency:go-offline](https://maven.apache.org/plugins/maven-dependency-plugin/go-offline-mojo.html): download everything the build will need, up front

## Why
Java services ship as a jar, and most teams build that jar inside Docker so the build does not depend on whose laptop it ran on. The naive Dockerfile runs on the Maven image and copies the whole project in. The image then carries a compiler, Maven, every source file and the downloaded dependencies of the build, none of which a running service needs, and each of which is something a scanner reports.

A multi-stage build splits the two jobs, as 297 did for Python. The build stage is Maven on a JDK. The runtime stage is a JRE, the part of Java that runs code and cannot compile it, and it receives exactly one file from the build: the jar.

The order inside the build stage matters as much as in 290. Maven downloads dependencies on the first build, which is slow. Copy `pom.xml` alone, run `mvn dependency:go-offline` to fetch everything it lists, and only then copy `src`. An edit to the code then reuses the downloaded dependencies from the layer cache, and only a change to the pom downloads again. `-B`, batch mode, keeps Maven from filling the build log with progress bars.

## You get
A build context with a small Java service: its `pom.xml` and its source under `src/`, open in the tabs above the editor. It builds `target/orders-1.0.0.jar`, and reads the port it listens on from `PORT`.

## You return
A Dockerfile that builds the jar with Maven on Java `{java}`, and runs it on a Java `{java}` JRE, listening on port `{port}`.

## Rules
- two stages. The first is `FROM maven:3.9-eclipse-temurin-{java} AS build`, with `WORKDIR /build`
- in it: copy `pom.xml`, then `RUN mvn -B dependency:go-offline`, then copy `src`, then `RUN mvn -B package`. No `COPY . .`
- the second is `FROM eclipse-temurin:{java}-jre`, with `WORKDIR /app`, and runs nothing
- it copies only `/build/target/orders-1.0.0.jar` from the build stage, to `/app/app.jar`
- `ENV PORT={port}`, `EXPOSE {port}`, and `ENTRYPOINT ["java", "-jar", "app.jar"]`

## Hints
### Hint 1
The build stage in the order the rules give, with a directory copied by naming it and its destination:

```dockerfile
COPY pom.xml .
RUN mvn -B dependency:go-offline
COPY src ./src
```

### Hint 2
`mvn package` writes the jar under `target/`, named from the pom's `artifactId` and `version`. `-DskipTests` is common here, on the grounds that CI has already run the tests; this pom has none either way.

### Hint 3
The runtime stage is four lines and an entrypoint. `--from` names the stage, the path is where Maven wrote the jar, and the jar gets a short name of its own:

```dockerfile
COPY --from=build /build/target/orders-1.0.0.jar app.jar
```
