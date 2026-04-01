stage('🔐 PR Vulnerability Scan (Gemini AI)') {
    steps {
        sh '''
        cd /home/ubuntu/abacux_data_visual/abacux_charts

        echo "📂 Getting changed files..."

        git fetch origin staging
        git diff --name-only origin/staging...HEAD > changed_files.txt

        echo "Changed files:"
        cat changed_files.txt

        echo "📄 Collecting code snippets..."

        > pr_code.txt
        while read file; do
            if [ -f "$file" ]; then
                echo "----- $file -----" >> pr_code.txt
                head -n 200 "$file" >> pr_code.txt
            fi
        done < changed_files.txt

        echo "🤖 Sending PR code to Gemini..."

        RESPONSE=$(curl -s -X POST \
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY" \
          -H "Content-Type: application/json" \
          -d "{
            \\"contents\\": [{
              \\"parts\\": [{
                \\"text\\": \\"Check this PR code for security vulnerabilities and risky patterns: $(cat pr_code.txt | head -c 3000)\\" 
              }]
            }]
          }")

        echo "$RESPONSE"

        if echo "$RESPONSE" | grep -i "critical"; then
            echo "❌ Critical issue found in PR"
            exit 1
        fi
        '''
    }
}