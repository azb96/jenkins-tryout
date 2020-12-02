pipeline {

    tools {
        maven 'apache-maven-3.6.3'
        jdk 'jdk8'
    }

    stages {
        stage ('Initialize') {
            steps {
                sh '''
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
                sh 'mvn -Dmaven.test.failure.ignore=true install'
            }
            post {
                success {
                    junit 'target/surefire-reports/**/*.xml'
                }
            }
        }
        stage('Build image') {
                /* This builds the actual image; synonymous to
                 * docker build on the command line */
                app = docker.build("jenkins-tryout")
        }
    }
}