variable "table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "hash_key" {
  description = "Hash key for the table"
  type        = string
}

variable "hash_key_type" {
  description = "Type of the hash key (S, N, B)"
  type        = string
  default     = "S"
}