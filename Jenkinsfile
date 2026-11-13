// Pipeline: Push/PR -> Build & Test -> (ผ่านเท่านั้น) Deploy -> Smoke test
pipeline {
  agent any
  environment {
    COMPOSE_PROJECT_NAME = 'pettech'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Unit/Integration Test') {
      steps {
        sh '''
          docker build -t pettech-backend-test --target test ./backend
          docker run --rm pettech-backend-test
        '''
      }
    }
    stage('Build Images') {
      steps { sh 'docker compose build' }
    }
    stage('Deploy') {
      steps {
        sh '''
          test -f .env || cp .env.example .env
          docker compose up -d --wait
        '''
      }
    }
    stage('Smoke Test') {
      steps { sh 'bash ./scripts/smoke-test.sh' }
    }
  }
  post {
    failure {
      sh 'docker compose logs --tail=100 || true'
      echo 'Pipeline failed: หยุดการส่งมอบและบันทึกเป็น Defect'
    }
  }
}
