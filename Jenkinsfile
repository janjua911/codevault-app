pipeline {
    agent any

    options {
        cleanWs()   // ← Wipes workspace before each build (fixes permission errors)
    }

    triggers {
        pollSCM('* * * * *')   // Poll GitHub every minute for new pushes
    }

    environment {
        APP_IMAGE   = "codevault:latest"
        APP_CONTAINER = "codevault-app"
        TEST_REPO   = "https://github.com/janjua911/codevault-tests.git"
        // Docker image with Python 3.9 + Chrome + ChromeDriver + Selenium pre-installed
        TEST_IMAGE  = "joyzoursky/python-chromedriver:3.9-selenium"
    }

    stages {

        // ── 1. Checkout ────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📦 Checking out application code from GitHub...'
                checkout scm

                // Capture the email of whoever pushed this commit
                script {
                    env.PUSHER_EMAIL = sh(
                        script: "git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()
                    echo "📧 Push made by: ${env.PUSHER_EMAIL}"
                }
            }
        }

        // ── 2. Build ────────────────────────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image for CodeVault...'
                sh "docker build -t ${APP_IMAGE} ."
            }
        }

        // ── 3. Deploy ───────────────────────────────────────────────────────
        stage('Run Application') {
            steps {
                echo '🚀 Starting Flask application container...'
                sh """
                    docker stop ${APP_CONTAINER} 2>/dev/null || true
                    docker rm   ${APP_CONTAINER} 2>/dev/null || true
                    docker run -d \\
                        --name ${APP_CONTAINER} \\
                        --network host \\
                        ${APP_IMAGE}
                    echo "⏳ Waiting for Flask to be ready..."
                    sleep 8
                """
            }
        }

        // ── 4. Test ─────────────────────────────────────────────────────────
        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium test suite...'
                sh """
                    # Clone the test repository into workspace
                    git clone ${TEST_REPO} test-suite

                    # Run tests inside Docker container
                    # - Mount only the test folder
                    # - Use --network host so Selenium can reach localhost:5000
                    # - Generate JUnit XML for Jenkins test reporting
                    docker run --rm \\
                        --network host \\
                        -v ${WORKSPACE}/test-suite:/tests \\
                        -w /tests \\
                        ${TEST_IMAGE} \\
                        bash -c "pip install pytest pytest-html --quiet && \\
                                 python -m pytest test_codevault.py -v \\
                                 --junitxml=results.xml \\
                                 --html=report.html --self-contained-html"
                """
            }

            // Publish JUnit results in Jenkins UI
            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'test-suite/results.xml'
                }
            }
        }
    }

    // ── Post-build actions ──────────────────────────────────────────────────
    post {

        always {
            echo '🧹 Cleaning up application container...'
            sh """
                docker stop ${APP_CONTAINER} 2>/dev/null || true
                docker rm   ${APP_CONTAINER} 2>/dev/null || true
            """
        }

        success {
            echo '✅ All tests passed!'

            emailext(
                to: "${env.PUSHER_EMAIL}",
                subject: "✅ [CodeVault CI] Build #${BUILD_NUMBER} — ALL TESTS PASSED",
                body: """
<html>
<body style="font-family:monospace; background:#050810; color:#c8d8e8; padding:20px;">
  <h2 style="color:#00f5c4;">✅ CodeVault Pipeline SUCCESS</h2>
  <table style="border-collapse:collapse; width:100%">
    <tr><td style="padding:6px; color:#4a5a72;">Build Number</td><td style="color:#fff;">#${BUILD_NUMBER}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Status</td><td style="color:#00f5c4;"><b>SUCCESS — All Tests Passed</b></td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Branch</td><td style="color:#fff;">${GIT_BRANCH}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Commit</td><td style="color:#fff;">${GIT_COMMIT.take(10)}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Triggered by</td><td style="color:#fff;">${env.PUSHER_EMAIL}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Duration</td><td style="color:#fff;">${currentBuild.durationString}</td></tr>
  </table>
  <br/>
  <p><a href="${BUILD_URL}" style="color:#0ea5e9;">🔗 View Full Build Log</a></p>
  <p><a href="${BUILD_URL}testReport" style="color:#0ea5e9;">📊 View Test Report</a></p>
  <hr style="border-color:#1a2a3a;"/>
  <small style="color:#4a5a72;">CodeVault CI — COMSATS University DevOps Assignment</small>
</body>
</html>
                """,
                mimeType: 'text/html',
                attachmentsPattern: 'test-suite/report.html'
            )
        }

        failure {
            echo '❌ Build or tests failed!'

            emailext(
                to: "${env.PUSHER_EMAIL}",
                subject: "❌ [CodeVault CI] Build #${BUILD_NUMBER} — FAILED",
                body: """
<html>
<body style="font-family:monospace; background:#050810; color:#c8d8e8; padding:20px;">
  <h2 style="color:#ff3366;">❌ CodeVault Pipeline FAILED</h2>
  <table style="border-collapse:collapse; width:100%">
    <tr><td style="padding:6px; color:#4a5a72;">Build Number</td><td style="color:#fff;">#${BUILD_NUMBER}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Status</td><td style="color:#ff3366;"><b>FAILED</b></td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Branch</td><td style="color:#fff;">${GIT_BRANCH}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Commit</td><td style="color:#fff;">${GIT_COMMIT.take(10)}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Triggered by</td><td style="color:#fff;">${env.PUSHER_EMAIL}</td></tr>
    <tr><td style="padding:6px; color:#4a5a72;">Duration</td><td style="color:#fff;">${currentBuild.durationString}</td></tr>
  </table>
  <br/>
  <p><a href="${BUILD_URL}console" style="color:#0ea5e9;">🔍 View Console Output</a></p>
  <hr style="border-color:#1a2a3a;"/>
  <small style="color:#4a5a72;">CodeVault CI — COMSATS University DevOps Assignment</small>
</body>
</html>
                """,
                mimeType: 'text/html'
            )
        }
    }
}
