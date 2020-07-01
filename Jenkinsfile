pipeline {
    agent {
        docker { 
            image 'devcontainer:latest' 
        }
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '60'))
        timeout(time: 4, unit: 'HOURS')
        //skipDefaultCheckout()
    }

    parameters {
        string(name: 'CF_URL', defaultValue: 'https://api.run.pivotal.io',
            description: '''
                Using PCF Cloudfoundry
            ''')
        string(name: 'CF_ORG', defaultValue: 'SANNV',
            description: '''
                Using PCF Cloudfoundry
            ''')
        string(name: 'CF_SPACE', defaultValue: 'development', description: 'CF space. eg: jenkins ?')
        string(name: 'PREFIX', defaultValue: '', description: 'usually same as CF_SPACE. Empty = Dynamic generation')
        string(name: 'CF_CRED_ID', defaultValue: '62f9ef52-e601-4543-a0db-f5eda2210c31', description: 'get it from jenkins credentials')
        string(name: 'NUM_USERS', defaultValue: '20', description: 'Total number of concurrent users')
        string(name: 'HOLD_HOURS', defaultValue: '0.5',  description: 'Total amount of time to execute the tests')
    }

	environment {
		CF_HOME = "${env.WORKSPACE}"
	}

    stages {
        stage('Prepare Dev Env') {
            parallel {
                stage('Create Dev Conda Env'){
                    steps {
                        sh '''#!/bin/bash
                            conda env create -f environment_dev.yml
                        '''
                    }                    
                }
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

            }
        }

        stage('Unit Test') {
            steps {
				sh '''#!/bin/bash
                    source activate namekoexample
                    ./dev_pytest.sh
				'''
            }
        }

        stage('Smoke Test') {
            steps {
				sh '''#!/bin/bash
                    source activate namekoexample
                    echo "Start app service ..."
                    ./dev_run.sh gateway.service orders.service products.service > app.log &
                    sleep 5
                    echo "Start smoketest ..."
                    ./devops/nex-smoketest.sh local
				'''
            }
        }

        stage('Deploy + Test') {

            stages {

                stage('Deploy') {
                    when {
                        anyOf {
                                expression{ env.BRANCH_NAME =~ 'dockerTest0' }
                                branch 'performance'
                                branch 'master'
                        }
                    }

                    steps {
                        script {
                            if (!params.PREFIX?.trim()) {
                                env.PREFIX = sh(returnStdout: true, script: 'echo ${BUILD_TAG} | md5sum | cut -c -10').trim()
					        }
                        }
					    // cf login and undeploy
                        withCredentials([[$class: 'UsernamePasswordMultiBinding',
                            credentialsId: "${params.CF_CRED_ID}",
                            usernameVariable: 'CF_USR', passwordVariable: 'CF_PWD']]){

                                sh '''#!/bin/bash
                                    set -e
                                    echo "Deploy: CF Login into org:${CF_ORG}, space:${CF_SPACE}"
                                    cf login -u ${CF_USR} -p ${CF_PWD} -a ${CF_URL} -o ${CF_ORG} -s ${CF_SPACE}
                                    source activate namekoexample
                                    echo "Deploy: nex-deploy.sh ${PREFIX}"
                                    ./devops/nex-deploy.sh ${PREFIX}
                                '''
                        }
                    }
                }

                stage('Smoke Test on CF') {
                    steps {
                        sh '''#!/bin/bash
                            source activate namekoexample
                            echo "Start app service ..."
                            ./dev_run.sh gateway.service orders.service products.service > app.log &
                            sleep 5
                            echo "Start smoketest ..."
                            ./devops/nex-smoketest.sh local
                        '''
                    }
                }                
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
			archiveArtifacts allowEmptyArchive: true, artifacts: '**/*.log', fingerprint: true
            deleteDir()
		}
    }
}