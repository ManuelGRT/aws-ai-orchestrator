aws-login:
	aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 435772683141.dkr.ecr.eu-west-1.amazonaws.com

docker-build:
	docker build -t denoising-ai-api-repository .

docker-tag:
	docker tag denoising-ai-api-repository:latest 435772683141.dkr.ecr.eu-west-1.amazonaws.com/denoising-ai-api-repository:latest

docker-push:
	docker push 435772683141.dkr.ecr.eu-west-1.amazonaws.com/denoising-ai-api-repository:latest