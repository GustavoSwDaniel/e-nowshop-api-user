pipeline {
    agent any  
    environment {
        PROJECT_ID = 'enowhop'
        REGISTRY_URL = "gcr.io/${PROJECT_ID}"
        IMAGE_NAME = 'enowsho-api-user'
        TAG_NAME = "latest"
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
                        gcloud auth configure-docker --quiet
                        docker push $REGISTRY_URL/$IMAGE_NAME:$TAG_NAME
                    ''' 
                }
            }
        }
        stage('Apply Kubernetes files') {
            steps {
                withKubeConfig([credentialsId: 'kubeconfig']){
                    sh "kubectl set image -f ./cid/deployment.yaml enowshop-api-user=${HOSTNAME}/${PROJECT_ID}/${IMAGE_NAME}:${TAG_NAME}"
                }
            }
        }
    }
}
