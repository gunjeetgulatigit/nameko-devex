pipeline {
    agent {
        docker { 
            image 'devcontainer:latest' 
            // args '--user root'
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
                    source activate namekoexample
                    nameko -h
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