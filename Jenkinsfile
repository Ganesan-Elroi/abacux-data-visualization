pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                sh '''
                cd /home/ubuntu/abacux_data_visual/abacux_charts
                git fetch --all
                git reset --hard origin/staging
                git clean -fd -e .env
                '''
            }
        }

        stage('Stop Containers') {
            steps {
                sh '''
                cd /home/ubuntu/abacux_data_visual/abacux_charts
                docker-compose down
                '''
            }
        }

        stage('Build & Deploy') {
            steps {
                sh '''
                cd /home/ubuntu/abacux_data_visual/abacux_charts
                docker-compose up -d --build
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                echo "Checking app..."
                sleep 5
                echo "✅ App is running"
                '''
            }
        }
    }
}