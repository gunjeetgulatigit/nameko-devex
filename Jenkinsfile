pipeline {
    agent {
        docker { image 'linuxbrew/linuxbrew' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'brew install git'
                sh 'git clone https://github.com/nameko/nameko-examples'
            }
        }
    }
}