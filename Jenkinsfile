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
                    dockerapp = docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}", ".")
                }
            }
        }
        stage ('Publish to GCR') {
            steps {
               script{
                    withDockerRegistry([credentialsId: "gcr: ${params.GCP_PROJECT_ID}", url: "https://gcr.io"]){
                        sh "docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG_NAME}"
                    }
               }
            }
        }
    }
}