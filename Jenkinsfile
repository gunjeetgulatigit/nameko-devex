pipeline {
    agent {
        docker { 
            image 'devcontainer:dev' 
        }
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '60'))
        timeout(time: 4, unit: 'HOURS')
        //skipDefaultCheckout()
    }

    parameters {
        string(name: 'CF_URL', defaultValue: 'https://api.dev.kubecf.speedyorbit.com',
            description: '''
                Using KubeCF
            ''')
        string(name: 'CF_ORG', defaultValue: 'good',
            description: '''
                Using PCF Cloudfoundry
            ''')
        string(name: 'CF_SPACE', defaultValue: 'morning', description: 'CF space. eg: jenkins ?')
        string(name: 'PREFIX', defaultValue: '', description: 'usually same as CF_SPACE. Empty = Dynamic generation')
        string(name: 'CF_CRED_ID', defaultValue: 'ddb7804d-3dbf-48fc-8b14-7ddaa6fc2ea2', description: 'get it from jenkins credentials')
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
                        script {
                            if (currentBuild.number == 1) {
                                build(job: currentBuild.fullProjectName, propagate: false, wait: false)
                                currentBuild.result = "ABORTED"
                                error("Job #1: aborting and re-build for initialize parameters")
                            }

                            if (!params.PREFIX?.trim()) {
                                env.PREFIX = sh(returnStdout: true, script: 'echo ${BUILD_TAG} | md5sum | cut -c -10').trim()
                            }
                        }      
                                           
                        sh '''#!/bin/bash
                            conda env create -f environment_dev.yml > conda_create.log
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
                            echo "Starting Postgres Service"
                            # source activate ${HOME}/.conda/envs/postgres
                            source activate postgres
                            DB_DIR=$(mktemp -d -t postgres.XXX)
                            echo ${DB_DIR}
                            INIT_DB_PATH=${HOME}/.conda/envs/postgres/share
                            echo ${INIT_DB_PATH}

                            initdb -L ${INIT_DB_PATH} -D ${DB_DIR}/postgres

                            # Configure pg_hdb.conf file
                            echo "host    all             all             0.0.0.0/0            trust" >> ${DB_DIR}/postgres/pg_hba.conf
                            echo "host    replication             all             0.0.0.0/0            trust" >> ${DB_DIR}/postgres/pg_hba.conf
                            echo "port = 5432" >> ${DB_DIR}/postgres/my_custom.conf
                            echo "listen_addresses = '0.0.0.0'" >> ${DB_DIR}/postgres/my_custom.conf
                            echo "include = 'my_custom.conf'" >> ${DB_DIR}/postgres/postgresql.conf

                            postgres -i -N 200 -D ${DB_DIR}/postgres &

                            sleep 5
                            createuser --no-password --superuser postgres
                            # createdb --owner=postgres postgres
                            echo "GRANT CONNECT ON DATABASE postgres TO postgres;" | psql postgres
                            echo "Users and local db is created..."
                        '''
                    }
                }

            }
        }

        stage('Unit Test') {
            steps {
				sh '''#!/bin/bash
                    source activate nameko-devex
                    ./dev_pytest.sh
				'''
            }
        }

        stage('Smoke Test') {
            steps {
				sh '''#!/bin/bash
                    source activate nameko-devex
                    echo "Start app service ..."
                    FASTAPI=X ./dev_run.sh orders.service products.service > app.log &
                    sleep 5
                    echo "Start smoketest ..."
                    ./test/nex-smoketest.sh local
				'''
            }
        }

        stage('Deploy + Test') {

            when {
                anyOf {
                    expression{ env.BRANCH_NAME =~ 'PR-' }
                    branch 'performance'
                    branch 'master'
                }
            }

            stages {

                stage('Deploy') {

                    steps {
					    // cf login and undeploy
                        withCredentials([[$class: 'UsernamePasswordMultiBinding',
                            credentialsId: "${params.CF_CRED_ID}",
                            usernameVariable: 'CF_USR', passwordVariable: 'CF_PWD']]){

                                sh '''#!/bin/bash
                                    echo "Deploy: CF Login into org:${CF_ORG}, space:${CF_SPACE}"
                                    cf login -u ${CF_USR} -p ${CF_PWD} -a ${CF_URL} -o ${CF_ORG} -s ${CF_SPACE}
                                    source activate nameko-devex
                                    set -e
                                    echo "Deploy: CF_APP=${PREFIX} make deployCF"
                                     CF_APP=${PREFIX} make deployCF > deploy.log
                                '''
                        }
                    }
                }

                stage('Smoke Test on CF') {
                    steps {
                        sh '''#!/bin/bash
                            source activate nameko-devex
                            echo "Start smoketest ..."
                            ./test/nex-smoketest.sh https://${PREFIX}.dev.kubecf.speedyorbit.com
                        '''
                    }
                }

                stage('Perf Test') {

                    when {
                        anyOf {
                            branch 'performance'
                            branch 'master'
                        }
                    }

                    steps {
                        sh '''#!/bin/bash
                            source activate nameko-devex
                            echo "Start perftest ..."
                            ./test/nex-bzt.sh https://${PREFIX}.dev.kubecf.speedyorbit.com
                        '''
                    }

                }             
            }
        }
    }

    post {
		always {
			script {
				// undeploy first if deployed
                if (fileExists('deploy.log')) {
                    sh '''
                        echo "post: Undeploy landscape: ${PREFIX}"
                        CF_APP=${PREFIX} make undeployCF
                    '''
                }
			}
		}

		cleanup {
			archiveArtifacts allowEmptyArchive: true, artifacts: '**/*.log, *.xng', fingerprint: true
            deleteDir()

		}
    }
}