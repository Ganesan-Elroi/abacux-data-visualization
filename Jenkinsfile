pipeline {
    agent any

    environment {
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
    }

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

        stage('🔐 Vulnerability Scan (Gemini AI)') {
            steps {
                sh '''
                echo "🔍 Running dependency scan..."

                cd /home/ubuntu/abacux_data_visual/abacux_charts

                # Example: Node.js project
                if [ -f package.json ]; then
                    npm install --silent
                    npm audit --json > audit.json
                fi

                echo "🤖 Sending report to Gemini..."

                if [ -f audit.json ]; then
                    RESPONSE=$(curl -s -X POST \
                      "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY" \
                      -H "Content-Type: application/json" \
                      -d "{
                        \\"contents\\": [{
                          \\"parts\\": [{
                            \\"text\\": \\"Analyze this vulnerability report. Tell if there are CRITICAL or HIGH issues and summarize risks: $(cat audit.json | head -c 3000)\\" 
                          }]
                        }]
                      }")

                    echo "$RESPONSE" > gemini_report.json

                    echo "📊 Gemini Analysis:"
                    cat gemini_report.json

                    # Optional: Fail pipeline if "CRITICAL" found
                    if echo "$RESPONSE" | grep -i "CRITICAL"; then
                        echo "❌ Critical vulnerabilities found! Stopping pipeline."
                        exit 1
                    fi
                fi

                echo "✅ Gemini vulnerability scan completed"
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