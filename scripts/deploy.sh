#!/bin/bash
set -e

minikube status > /dev/null 2>&1 || minikube start --driver=docker
minikube addons enable metrics-server

docker build -t utkarsh01saxena/flask-mongodb-app:latest ./flask-mongodb-app
minikube image load utkarsh01saxena/flask-mongodb-app:latest

kubectl apply -f k8s/complete-deployment.yaml

kubectl rollout status statefulset/mongodb --timeout=120s
kubectl rollout status deployment/flask-deployment --timeout=120s

echo "Deployment completed successfully."
minikube service flask-service
