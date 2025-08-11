# LocalStack Python Lambda Demo

This project demonstrates deploying a Python AWS Lambda function to LocalStack using Terraform.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Terraform (v1.0+)
- Docker Desktop (for LocalStack)
- AWS CLI (for testing)

## Setup Instructions

### 1. Install Docker Desktop

1. Download Docker Desktop for Mac from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Open the downloaded `.dmg` file and drag Docker.app to your Applications folder
3. Start Docker Desktop from your Applications folder
4. (Optional) Add Docker CLI to your PATH by adding this to your `~/.zshrc` or `~/.bash_profile`:
   ```bash
   export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
   ```
   Then run:
   ```bash
   source ~/.zshrc  # or source ~/.bash_profile
   ```
5. Verify Docker is working:
   ```bash
   docker --version
   docker run hello-world
   ```

### 2. Install Required Tools

1. **Install Python 3.9+** (if not already installed):
   ```bash
   brew install python@3.9
   ```

2. **Install Terraform** (if not already installed):
   ```bash
   brew install terraform
   ```

3. **Install AWS CLI** (if not already installed):
   ```bash
   brew install awscli
   ```

4. **Install LocalStack** (Python package):
   ```bash
   pip install localstack
   ```

### 3. Clone the Repository

```bash
git clone https://github.com/Amivero-LLC/lambda_demo.git
cd lambda_demo
```

### 4. Start LocalStack

In a terminal window, start LocalStack with the required services:

```bash
docker compose up -d
```

### 5. Deploy the Lambda Function

In a new terminal window, navigate to the project directory and run:

```bash
# Initialize Terraform
make init

# Deploy the Lambda function
make apply
```

### 6. Test the Lambda Function

```bash
make test
```

This will invoke the Lambda function and display the output.

## Project Structure

- `lambda/` - Contains the Lambda function code and dependencies
  - `lambda_function.py` - Main Lambda function code
  - `requirements.txt` - Python dependencies
- `main.tf` - Terraform configuration for the Lambda function
- `variables.tf` - Terraform variable definitions
- `Makefile` - Helper commands for common tasks

## Cleanup

To remove all resources:

```bash
make destroy
```

## Troubleshooting

- **Docker not found**: Ensure Docker Desktop is running and the Docker CLI is in your PATH
- **Port conflicts**: If you get port errors, make sure no other services are using ports 4566 or 4510-4559
- **Lambda execution issues**: Check the LocalStack logs for detailed error messages

## License

This project is licensed under the MIT License.