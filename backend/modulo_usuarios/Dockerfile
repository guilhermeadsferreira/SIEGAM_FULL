# Use uma imagem base com Java
FROM registry.access.redhat.com/ubi9/openjdk-21:1.23

WORKDIR /app

COPY target/quarkus-app/ /app/
EXPOSE 8002

CMD ["java", "-jar", "/app/quarkus-run.jar"]
