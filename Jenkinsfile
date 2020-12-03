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
                bat 'mvn install'
            }
            post {
                success {
                    junit 'target/surefire-reports/**/*.xml'
                }
            }
        }
         stage('build && SonarQube analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    withMaven(maven: 'apache-maven-3.6.3') {
                        bat 'mvn sonar:sonar'
                    }
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
