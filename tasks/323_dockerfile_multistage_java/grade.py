"""What one sitting of 323 asks for, and what counts as having answered it.

`check` follows the jar: the build stage resolves the dependencies from the pom alone,
then builds from the source, and the runtime stage takes the jar and nothing else."""

JAVAS = ["17", "21"]
JAR = "orders-1.0.0.jar"


def brief(r):
    return {"java": r.choice(JAVAS), "port": r.choice([8080, 8081, 9000])}


def _all(stage, cmd):
    return [s for s in stage["steps"] if s["cmd"] == cmd]


def _mvn(stage, goal):
    return [s for s in _all(stage, "RUN") if s["words"][:1] == ["mvn"] and goal in s["words"]]


def check(stages, b):
    assert len(stages) == 2, f"two stages, one to build and one to run: this file has {len(stages)}"
    build, final = stages
    base = f"maven:3.9-eclipse-temurin-{b['java']}"
    assert build["base"] == base, (
        f"line {build['line']}: build FROM {base}, Maven on the JDK the app targets"
    )
    assert build["name"], "name the build stage, `FROM ... AS build`, so the next one can copy from it"
    workdir = [w for s in _all(build, "WORKDIR") for w in s["words"]]
    assert workdir == ["/build"], "WORKDIR /build in the build stage"
    offline = _mvn(build, "dependency:go-offline")
    package = _mvn(build, "package")
    assert offline, "resolve the dependencies first: `RUN mvn -B dependency:go-offline`"
    assert package, "build the jar: `RUN mvn -B package`"
    copies = _all(build, "COPY")
    pom = [c for c in copies if c["words"][:1] == ["pom.xml"]]
    src = [c for c in copies if c["words"][:1] in (["src"], ["src/"])]
    assert pom and pom[0]["line"] < offline[0]["line"], (
        "copy pom.xml on its own, before the dependencies are resolved from it"
    )
    assert src and offline[0]["line"] < src[0]["line"] < package[0]["line"], (
        "copy src after resolving the dependencies and before packaging, so an edit to the "
        "code reuses the downloaded dependencies"
    )
    assert not [c for c in copies if "." in c["words"][:-1]], (
        "copy pom.xml and src by name: `COPY . .` puts every file in the context into the "
        "cache key of the step that downloads the dependencies"
    )
    for step in (*offline, *package):
        assert "-B" in step["words"] or "--batch-mode" in step["words"], (
            f"line {step['line']}: run Maven with -B, or its progress bars fill the build log"
        )

    runtime = f"eclipse-temurin:{b['java']}-jre"
    assert final["base"] == runtime, (
        f"line {final['line']}: run FROM {runtime}: a JRE runs the jar, and the JDK and "
        "Maven stay behind in the build stage"
    )
    assert not _all(final, "RUN"), "the runtime stage builds nothing: it only receives the jar"
    copied = [c for c in _all(final, "COPY") if c["flags"].get("from") == build["name"]]
    assert len(copied) == 1, f"copy the jar `--from={build['name']}`, and only the jar"
    assert copied[0]["words"][0] == f"/build/target/{JAR}", (
        f"line {copied[0]['line']}: the jar Maven builds is /build/target/{JAR}"
    )
    assert not [c for c in _all(final, "COPY") if not c["flags"].get("from")], (
        "the runtime stage copies nothing from the context: the jar holds the app"
    )
    workdir = [w for s in _all(final, "WORKDIR") for w in s["words"]]
    assert workdir == ["/app"], "WORKDIR /app in the runtime stage"
    assert copied[0]["words"][-1] in ("app.jar", "/app/app.jar"), (
        f"line {copied[0]['line']}: copy the jar to /app/app.jar"
    )
    entry = _all(final, "ENTRYPOINT")
    assert len(entry) == 1 and entry[0]["exec"], "one ENTRYPOINT, in exec form"
    run = entry[0]["exec"]
    assert run in (["java", "-jar", "app.jar"], ["java", "-jar", "/app/app.jar"]), (
        f'line {entry[0]["line"]}: ENTRYPOINT ["java", "-jar", "app.jar"]'
    )
    env = [w for s in _all(final, "ENV") for w in s["words"]]
    assert f"PORT={b['port']}" in env, f"the app reads its port from PORT: `ENV PORT={b['port']}`"
    exposed = [w for s in _all(final, "EXPOSE") for w in s["words"]]
    assert exposed in ([str(b["port"])], [f"{b['port']}/tcp"]), f"EXPOSE {b['port']}"
