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
        stage ('Load Docker') {
            steps {
                script {
                    def dockerCommons = Jenkins.instance.getPlugin("docker-commons")
                    dockerCommons.getDescriptor().getCheck().execute(new LogTaskListener(LOGGER, Level.INFO))
                }
            }
        }
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
                    withRegistry([credentialsId: "gcr: [${CREDENTIALS_ID}]", url: 'https://gcr.io']) {
                        docker.image("${REGISTRY_URL}/${IMAGE_NAME}:${TAG_NAME}").push()
                    }
                }
            }
        }
    }
}
