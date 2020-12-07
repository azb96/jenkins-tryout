FROM maven:3.6.3-openjdk-8 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY . .
RUN mvn install -DskipTests
FROM openjdk:8u171-jre-alpine
COPY --from=builder /build/target/*.jar /app/firstproject.jar
EXPOSE 8090
ENTRYPOINT [ "java", "-jar", "/app/firstproject.jar" ]



