variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "interstellar-route-planner"
}

variable "app_repo" {
  description = "Git repository URL for the application"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Amazon Linux 2023)"
  type        = string
  default     = "ami-0c02fb55956c7d316" # Amazon Linux 2023 in us-east-1
}
