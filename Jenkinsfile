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

        stage ('Build') {
            environment {
                HOME="."
            }
            steps {
                bat 'mvn -Dmaven.test.failure.ignore=true install'
            }
            post {
                success {
                    junit 'target/surefire-reports/**/*.xml'
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
