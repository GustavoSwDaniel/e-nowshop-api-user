pipeline {
    agent any  
    environment {
        PROJECT_ID = 'enowhop'
        REGISTRY_URL = "gcr.io/${PROJECT_ID}"
        IMAGE_NAME = 'enowsho-api-user'
        TAG_NAME = "${env.BUILD_ID}"
        CREDENTIALS_ID = "enowhop"
        HOSTNAME = "gcr.io"
    }

    stages {
        stage ('Build image') {
            steps {
                script {
                    dockerapp = docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}", ".")
                }
            }
        }
        stage ('Publish to GCR') {
            steps {
                withCredentials([file(credentialsId: 'enowhop2', variable: 'ENOWSHOP2')]){
                    sh '''

                        gcloud auth activate-service-account --key-file="$ENOWSHOP2"
                        gcloud config set project $PROJECT_ID
                        at $ENOWSHOP2 | docker login -u _json_key --password-stdin https://$HOSTNAME
                        docker push $REGISTRY_URL/$IMAGE_NAME:$TAG_NAME
                    '''
                }
            }
        }
    }
}
