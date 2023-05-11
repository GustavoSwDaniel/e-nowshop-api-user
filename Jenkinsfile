pipeline {
    agent any  
    environment {
        PROJECT_ID = 'enowhop'
        REGISTRY_URL = "gcr.io/${PROJECT_ID}"
        IMAGE_NAME = 'enowsho-api-user'
        TAG_NAME = "${env.BUILD_ID}"
        CREDENTIALS_ID = "enowhop"
    }

    stages {
        stage ('Build image') {
            steps {
                script {
                    sh '''
                        gcloud version
                    '''
                    dockerapp = docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}", ".")
                }
            }
        }
        stage ('Publish to GCR') {
            steps {
                withCredentials([file(credentialsId: 'enowhop2', variable: 'ENOWSHOP2')]){
                    sh '''
                        echo $ENOWSHOP2
                        gcloud version
                        gcloud auth configure-docker --key-file="$ENOWSHOP2"
                        gcloud config set project $PROJECT_ID
                        docker push $REGISTRY_URL/$IMAGE_NAME:$TAG_NAME
                    '''
                }
            }
        }
    }
}
