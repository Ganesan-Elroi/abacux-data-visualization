pipeline {
    agent any

    stages {

        stage('Deploy Staging') {
            steps {
                sh '''
                echo "🚀 Deploying staging..."

                cd /home/ubuntu/abacux_data_visual/abacux_charts

                git fetch --all
                git reset --hard origin/staging
                git clean -fd -e .env

                docker-compose down
                docker-compose up -d --build

                echo "✅ Deployment complete"
                '''
            }
        }
    }
}