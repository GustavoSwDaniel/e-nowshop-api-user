pipeline {
    agent any  
    environment {
        PROJECT_ID = 'enowhop'
        REGISTRY_URL = "gcr.io/${PROJECT_ID}"
        IMAGE_NAME = 'enowsho-api-user'
        TAG_NAME = "${env.BUILD_ID}"
        CREDENTIALS_ID = "enowhop"
        CLOUDSDK_CORE_PROJECT='enowhop'
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
                withCredtials(file(credentialsId: 'enowhop2', variable: 'ENOWSHOP'))
                    sh '''
                        gcloud version
                        gcloud auth activate-service-account --key-file="${ENOWSHOP}
                        gcloud compute zones list
                    '''
            }
        }
    }
}
