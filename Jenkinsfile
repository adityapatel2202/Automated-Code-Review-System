pipeline {
    agent any

    // Trigger automatic GitHub Webhook deployment build
    triggers {
        githubPush()
    }

    environment {
        AWS_ACCOUNT_ID = '811430801569'
        AWS_DEFAULT_REGION = 'eu-west-2'
        ECR_REPO_NAME = 'automated-code-reviewer'
        EC2_IP = '3.11.103.59'
        EC2_USER = 'ubuntu'
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
                    pip install -r requirements.txt
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
                        # Authorize Security Group ingress rule for DB access from EC2
                        aws ec2 authorize-security-group-ingress --group-id sg-09e583b8dce41580a --protocol tcp --port 5432 --source-group sg-024dffcf930c79d0f --region ${AWS_DEFAULT_REGION} || true

                        # Ensure ECR repository exists
                        aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${AWS_DEFAULT_REGION} || true

                        # Login, Tag, and Push
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
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials-id'
                    ]]) {
                        sh '''
                            # Log EC2 Docker daemon into ECR using piped credentials from Jenkins
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} "sudo docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"

                            # Pull and run container on the EC2 host with SSL mode enabled for PostgreSQL
                            ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_IP} "
                                sudo docker stop app-reviewer || true &&
                                sudo docker rm app-reviewer || true &&
                                sudo docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest &&
                                sudo docker run -d -p 80:5000 \
                                  -e DATABASE_URL='postgresql://postgres:password@code-review-db.chasica08avl.eu-west-2.rds.amazonaws.com:5432/postgres?sslmode=require' \
                                  -e SECRET_KEY='your-secure-secret-key' \
                                  --name app-reviewer \
                                  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
                            "
                        '''
                    }
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
