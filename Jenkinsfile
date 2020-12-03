pipeline {
    agent any

    tools {
        maven 'apache-maven-3.6.3'
        jdk 'jdk8'
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
    }
}
