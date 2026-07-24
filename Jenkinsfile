pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = 'your-aws-account-id'
        AWS_DEFAULT_REGION = 'your-aws-region'
        ECR_REPO_NAME = 'automated-code-reviewer'
        EC2_IP = 'your-ec2-instance-ip'
        EC2_USER = 'ec2-user' // or 'ubuntu' depending on AMI
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing requirements...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Executing pytest suite...'
                sh '''
                    . venv/bin/activate
                    export PYTHONPATH=.
                    python -m pytest test_ai.py test_dataset.py -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker container image...'
                sh "docker build -t ${ECR_REPO_NAME}:latest ."
            }
        }

        stage('Push to AWS ECR') {
            steps {
                echo 'Logging into AWS ECR and pushing image...'
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-credentials-id'
                ]]) {
                    sh '''
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                        docker tag ${ECR_REPO_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
                        docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'SSH into EC2 and restarting docker container...'
                sshagent(['ec2-ssh-key-id']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} "
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com &&
                            docker stop app-reviewer || true &&
                            docker rm app-reviewer || true &&
                            docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest &&
                            docker run -d -p 80:5000 \
                              -e DATABASE_URL='postgresql://postgres:password@rds-endpoint:5432/postgres' \
                              -e SECRET_KEY='your-secure-secret-key' \
                              --name app-reviewer \
                              ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
                        "
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspaces...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please inspect Jenkins logs.'
        }
    }
}
