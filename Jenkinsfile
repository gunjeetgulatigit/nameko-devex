pipeline {
    agent {
        docker { image 'continuumio/miniconda3' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'conda env create -f environment_dev.yml'
                sh 'conda activate namekoexample'
            }
        }
    }
}