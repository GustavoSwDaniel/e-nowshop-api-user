pipeline {
    agent any  
    
    stages {
        stage ('Build image') {
            steps {
                script {
                    dockerapp = docker.build("enowsho-api-user:${env.BUILD_ID}")

                }
            }
        }
    }
}