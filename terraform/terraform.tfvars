# terraform.tfvars
# these values override the defaults set in main.tf
# i keep this file for local dev so i don't have to pass -var flags every time

app_name    = "taskflow"
environment = "production"
app_port    = 5000
replicas    = 1       # just one container for now, can increase later
image_tag   = "latest"
