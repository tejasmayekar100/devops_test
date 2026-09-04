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

                        export DATABASE_URL="sqlite:///test.db"
                        export JWT_SECRET_KEY="test-secret"
                        export FLASK_SECRET_KEY="test-secret"

                        python app.py > app.log 2>&1 &
                        APP_PID=$!

                        sleep 5

                        echo "========== APP LOG =========="
                        cat app.log || true
                        echo "============================="

                        if ! kill -0 $APP_PID 2>/dev/null; then
                            echo "Flask application failed to start"
                            exit 1
                        fi

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

    post {

        success {
            emailext(
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins Build Successful</h2>

                    <p>
                        The CI/CD pipeline completed successfully.
                    </p>

                    <p>
                        <b>Job:</b> ${env.JOB_NAME}<br>
                        <b>Build Number:</b> ${env.BUILD_NUMBER}<br>
                        <b>Build URL:</b> ${env.BUILD_URL}
                    </p>
                """,
                mimeType: 'text/html',
                to: "tejas70708080@gmail.com"
            )
        }

        failure {
            emailext(
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins Build Failed</h2>

                    <p>
                        The CI/CD pipeline failed.
                    </p>

                    <p>
                        <b>Job:</b> ${env.JOB_NAME}<br>
                        <b>Build Number:</b> ${env.BUILD_NUMBER}<br>
                        <b>Build URL:</b> ${env.BUILD_URL}
                    </p>
                """,
                mimeType: 'text/html',
                to: "tejas70708080@gmail.com"
            )
        }
    }
}