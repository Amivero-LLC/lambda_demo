.PHONY: init plan apply destroy clean test

init:
	@echo "Initializing Terraform..."
	@terraform init

plan: init
	@echo "Creating execution plan..."
	@terraform plan -out=tfplan

apply: plan
	@echo "Applying changes..."
	@terraform apply -auto-approve tfplan

destroy:
	@echo "Destroying resources..."
	@terraform destroy -auto-approve

clean:
	@echo "Cleaning up..."
	@rm -rf .terraform* terraform.tfstate* lambda.zip
	@echo "Clean complete!"

test:
	@echo "Testing Lambda function..."
	@echo '{"test": "python"}' > payload.json
	@aws --endpoint-url=http://localhost:4566 lambda invoke \
		--function-name $(shell terraform output -raw lambda_function_name) \
		--payload fileb://payload.json \
		--cli-binary-format raw-in-base64-out \
		output.json
	@cat output.json
	@echo ""
	@rm -f payload.json