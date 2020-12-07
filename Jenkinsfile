pipeline {
    agent any

    tools {
        maven 'apache-maven-3.6.3'
        jdk 'jdk8'
    }

    environment {
            NEXUS_VERSION = "nexus3.28.1-01"
            NEXUS_PROTOCOL = "http"
            NEXUS_URL = "127.0.0.1:8081"
            NEXUS_REPOSITORY = "first_project_release"
            NEXUS_CREDENTIAL_ID = "admin"
    }

    stages {
        stage ('Initialize') {
            steps {
                bat '''
                    echo "PATH = ${PATH}"
                    echo "M2_HOME = ${M2_HOME}"
                '''
            }
        }
        stage ('Test') {
            environment {
                HOME="."
            }
            steps {
                bat 'mvn test'
            }
        }

        stage ('Build') {
            environment {
                HOME="."
            }
            steps {
                bat 'mvn install -DskipTests=true'
            }
            post {
                success {
                    junit 'target/surefire-reports/**/*.xml'
                }
            }
        }
         stage('SonarQube analysis') {
            environment {
               HOME="."
            }
            steps {
                withSonarQubeEnv("SonarQube") {
                    bat 'mvn sonar:sonar'
                }
            }
         }
        stage('Building our image') {
             steps {
                  script {
                    dockerImage = docker.build("jenkins-tryout")
                  }
             }
        }

        stage("Publish to Nexus Repository Manager") {
              steps {
                    script {
                        docker tag jenkins-tryout localhost:8081/repository/firstproject:mytag
                        docker push localhost:8081/repository/firstproject:mytag
                    }
              }
        }
    }
}
