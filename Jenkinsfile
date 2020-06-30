pipeline {
    agent {
        docker { image 'continuumio/miniconda3' }
    }
    stages {
        stage('Test') {
            steps {
				sh '''#!/bin/bash
					cd /tmp
					git clone https://github.com/gitricko/nameko-examples
                    cd nameko-examples
                    conda env create -f environment_dev.yml
                    conda activate namekoexample
				'''
            }
        }
    }
}