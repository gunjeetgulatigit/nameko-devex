pipeline {
    agent {
        docker { image 'rabbitmq:3-management' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'echo "hello\\nasdasd\\n" | nc localhost 5672'
            }
        }
    }
}