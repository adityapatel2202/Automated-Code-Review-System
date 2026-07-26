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
                    python3 -m venv --system-site-packages venv
                    . venv/bin/activate
                    pip install -r requirements.txt --no-cache-dir
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Executing verification scripts...'
                sh '''
                    . venv/bin/activate
                    export PYTHONPATH=.
                    python test_ai.py
                    python test_dataset_loader.py
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
                        echo "=== SECURITY GROUPS ==="
                        aws ec2 describe-security-groups --region eu-west-2
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
