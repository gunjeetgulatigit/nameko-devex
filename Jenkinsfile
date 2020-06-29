pipeline {
    agent {
        docker { image 'rabbitmq:3-management' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'netstat -an | grep LISTEN'
            }
        }
    }
}