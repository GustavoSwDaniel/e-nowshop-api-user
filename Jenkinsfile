pipeline {
    agent any  
    environment {
        PROJECT_ID = 'enowhop'
        REGISTRY_URL = "gcr.io/${PROJECT_ID}"
        IMAGE_NAME = 'enowsho-api-user'
        TAG_NAME = "${env.BUILD_ID}"
    }

    stages {
        stage ('Build image') {
            steps {
                script {
                    dockerapp = docker.build("enowsho-api-user:${env.BUILD_ID}")
                }
            }
        }

        stage ('Push image'){
            steps {
                withCredentials([googleServiceAccount(credentialsId: 'container-registry', project:'enowhop')]{
                    script {
                        docker.withRegistry("${REGISTRY_URL}", 'gcr'){
                            def image = docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}")
                            image.push()
                        }
                    }
                }
            }           
        }
    }
}