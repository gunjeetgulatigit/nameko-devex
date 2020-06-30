pipeline {
    agent {
        docker { image 'continuumio/miniconda3' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'cd /tmp'
                sh 'git clone https://github.com/gitricko/nameko-examples'
            }
        }
    }
}