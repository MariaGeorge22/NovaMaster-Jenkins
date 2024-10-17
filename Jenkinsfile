pipeline {
    agent any

    environment {
        IMAGE_NAME = 'novaverse-jenkins'  // Replace with your Docker image name
        CONTAINER_NAME = 'novaverse'  // Replace with your Docker image name
    }

    stages {
        stage('Clone repository') {
            steps {
                // Checkout code from GitHub
                git url: 'https://github.com/MariaGeorge22/NovaMaster-Jenkins.git', branch: 'main'
            }
        }
        stage("Build App") {
            steps {
             script {
                    // Build the Docker image
                    def image = docker.build("${env.IMAGE_NAME}:latest") // Change "myapp" to your image name
                }
            }
        }
        stage("Run App") {
            steps {
              script {
                def containerExists = sh(script: "docker ps -a -q -f name=${env.CONTAINER_NAME}", returnStdout: true).trim()

                if (containerExists) {
                        // Stop and remove the existing container
                        sh "docker stop ${env.CONTAINER_NAME} || true"
                        sh "docker rm ${env.CONTAINER_NAME} || true"
                    }
                    // Run the Docker container
                    docker.image("${env.IMAGE_NAME}:latest").run("-d --name ${env.CONTAINER_NAME} -p 4000:8000")
                }
            }
        }
    }

    post {
        always {
            cleanWs()  // Clean workspace after the build
        }
    }
}
