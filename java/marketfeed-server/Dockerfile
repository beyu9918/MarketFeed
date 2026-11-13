FROM maven:3.9.9-eclipse-temurin-21 AS build

WORKDIR /workspace

COPY pom.xml ./
COPY src ./src

RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jdk

WORKDIR /app

COPY --from=build /workspace/target/marketfeed-server-1.0.0.jar /app/app.jar

EXPOSE 9001

CMD ["java", "-jar", "/app/app.jar"]
