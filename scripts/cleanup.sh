#!/bin/bash
kubectl delete namespace flask-mongo-app --ignore-not-found
kubectl delete pv mongo-pv --ignore-not-found
