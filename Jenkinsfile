pipeline {
    agent {
        docker { 
            image 'devcontainer:latest' 
        }
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '60'))
        timeout(time: 4, unit: 'HOURS')
        // skipDefaultCheckout()
    }

    parameters {
        string(name: 'CF_URL', defaultValue: 'https://api.run.pivotal.io',
            description: '''
                Using PCF Cloudfoundry
            ''')
        string(name: 'CF_ORG', defaultValue: 'Demo',
            description: '''
                Using PCF Cloudfoundry
            ''')
        string(name: 'CF_SPACE', defaultValue: 'Development', description: 'CF space. eg: jenkins ?')
        string(name: 'PREFIX', defaultValue: '', description: 'usually same as CF_SPACE. Empty = Dynamic generation')
        string(name: 'CF_CRED_ID', defaultValue: 'xxxx', description: 'get it from jenkins credentials')
        string(name: 'NUM_USERS', defaultValue: '20', description: 'Total number of concurrent users')
        string(name: 'HOLD_HOURS', defaultValue: '0.5',  description: 'Total amount of time to execute the tests')
    }

	environment {
		CF_HOME = "${env.WORKSPACE}"
	}

    stages {

        stage('Start Local BackServices') {
            steps {
				sh '''#!/bin/bash
                    echo "Starting RabbitMQ Service"
                    source activate rabbitmq
                    rabbitmq-server -detached
                    sleep 30
                    rabbitmq-plugins enable rabbitmq_management
                    rabbitmqctl add_user "rabbit" "rabbit"
                    rabbitmqctl set_user_tags rabbit administrator
                    rabbitmqctl set_permissions --vhost '/' 'rabbit' '.' '.' '.' 

                    echo "Starting Redis Service"
                    source activate redis
                    # get config file for version 5
                    curl -s https://raw.githubusercontent.com/antirez/redis/5.0/redis.conf > ./redis.conf
                    redis-server ./redis.conf  --daemonize yes
                    sleep 5
                    echo 'CONFIG Set "requirePass" ""' | redis-cli

                    echo "Starting Postgres Service"
                    su - devuser -c 'conda activate postgres && initdb -D /tmp/postgres && pg_ctl -D /tmp/postgres -l /tmp/logfile start'
                    su - devuser -c 'conda activate postgres && createuser --no-password --superuser postgres'
                    # createdb --owner=postgres postgres
                    su - devuser -c 'conda activate postgres && echo "GRANT CONNECT ON DATABASE postgres TO postgres;" | psql postgres'

				'''
            }
        }

        stage('Smoketest') {
            steps {
				sh '''#!/bin/bash
                    conda env create -f environment_dev.yml
                    source activate namekoexample
                    ./dev_run.sh gateway.service orders.service products.service &

                    netstat -an
                    exit 0
					// git clone https://github.com/gitricko/nameko-examples
                    // cd nameko-examples
                    // ls -lah
                    // whoami
                    // conda env create -f environment_dev.yml
                    // source activate namekoexample
                    // nameko -h
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