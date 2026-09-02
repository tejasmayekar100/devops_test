pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('project_1') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                dir('project_1') {
                    sh '''
                        . venv/bin/activate

                        python app.py > app.log 2>&1 &
                        APP_PID=$!

                        sleep 5

                        pytest

                        TEST_RESULT=$?

                        kill $APP_PID || true

                        exit $TEST_RESULT
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('project_1') {
                    sh 'docker build -t tejasmayekar100/flask-app:latest .'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push tejasmayekar100/flask-app:latest
                    '''
                }
            }
        }
    }
}