pipeline {
    agent any

    triggers {
        githubPush()
    }

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
                        pip install --upgrade pip
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

                        export DATABASE_URL=sqlite:///test.db
                        export JWT_SECRET_KEY=test-secret
                        export FLASK_SECRET_KEY=test-secret

                        python app.py > app.log 2>&1 &
                        APP_PID=$!

                        sleep 5

                        echo "========== APP LOG =========="
                        cat app.log
                        echo "============================="

                        kill -0 $APP_PID

                        pytest tests/test_authentication.py
                        TEST_RESULT=$?

                        kill $APP_PID

                        exit $TEST_RESULT
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('project_1') {
                    sh '''
                        docker build -t tejasmayekar100/flask-app:latest .
                    '''
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

    post {
        success {
            emailext(
                subject: "SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins Build Successful</h2>
                    <p><b>URL:</b> ${env.BUILD_URL}</p>
                """,
                to: "tejas70708080@gmail.com"
            )
        }

        failure {
            emailext(
                subject: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins Build Failed</h2>
                    <p><b>URL:</b> ${env.BUILD_URL}</p>
                """,
                to: "tejas70708080@gmail.com"
            )
        }
    }
}