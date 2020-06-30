pipeline {
    agent {
        docker { 
            image 'continuumio/miniconda3' 
            args '--user root'
        }
    }
    stages {
        stage('Test') {
            steps {
				sh '''#!/bin/bash
					git clone https://github.com/gitricko/nameko-examples
                    cd nameko-examples
                    ls -lah
                    whoami
                    conda env create -f environment_dev.yml
                    conda activate namekoexample
				'''
            }
        }
    }
    post {
		always {
			// script {
			// 	// undeploy first
			// 	sh '''
			// 		echo "post: Undeploy landscape: ${PREFIX}"
			// 		./devops/cf/pmc-undeploy.sh -f ${PREFIX}
			// 	'''
			// }
			// archiveArtifacts allowEmptyArchive: true, artifacts: '**/*.log', fingerprint: true
            deleteDir()
		}
    }
}