pipeline {
    agent {
        docker { image 'rabbitmq:3-management' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'echo "hello\n\asdasd\n" | nc localhost 5672'
            }
        }
    }
}