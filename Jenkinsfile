pipeline {
    agent {
        docker { image 'continuumio/miniconda3' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'conda update conda'
                sh 'ls -lah'
            }
        }
    }
}