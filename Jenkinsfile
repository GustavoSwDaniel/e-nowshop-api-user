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
                    dockerapp = docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}", ".")
                }
            }
        }
        stage ('Publish to GCR') {
            steps {
                script {
                    docker.withRegistry([credentialsId: "gcr: [${CREDENTIALS_ID}]", url: 'https://gcr.io']) {
                        docker.image("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}").push()
                    }
                }
            }
        }
    }
}
