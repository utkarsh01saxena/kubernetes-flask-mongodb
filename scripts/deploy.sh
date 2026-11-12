#!/bin/bash
set -e

minikube status > /dev/null 2>&1 || minikube start --driver=docker
minikube addons enable metrics-server

docker build -t utkarsh01saxena/flask-mongodb-app:latest ./flask-mongodb-app
minikube image load utkarsh01saxena/flask-mongodb-app:latest

kubectl apply -f k8s/00-namespace.yaml

kubectl create secret generic mongodb-secret \
  --namespace=flask-mongo-app \
  --from-literal=mongo-root-username=admin \
  --from-literal=mongo-root-password="M0ngo_Secur3_2026!#pAss" \
  --from-literal=mongo-db=flask_db \
  --from-literal=mongo-uri="mongodb://admin:M0ngo_Secur3_2026%21%23pAss@mongo-service.flask-mongo-app.svc.cluster.local:27017/flask_db?authSource=admin" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f k8s/complete-deployment.yaml

kubectl rollout status statefulset/mongodb -n flask-mongo-app --timeout=120s
kubectl rollout status deployment/flask-deployment -n flask-mongo-app --timeout=120s

minikube service flask-service -n flask-mongo-app
