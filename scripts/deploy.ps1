$ErrorActionPreference = "Stop"

& minikube status
if ($LASTEXITCODE -ne 0) {
    & minikube start --driver=docker
}

& minikube addons enable metrics-server

& docker build -t utkarsh01saxena/flask-mongodb-app:latest ./flask-mongodb-app
& minikube image load utkarsh01saxena/flask-mongodb-app:latest

& kubectl apply -f k8s/complete-deployment.yaml

& kubectl rollout status statefulset/mongodb --timeout=120s
& kubectl rollout status deployment/flask-deployment --timeout=120s

& minikube service flask-service
