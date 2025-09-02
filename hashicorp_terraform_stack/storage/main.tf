
resource "aws_s3_bucket" "frontend" {
  bucket = "frontend-static-assets"
  acl    = "public-read"
}

resource "aws_rds_instance" "db" {
  allocated_storage    = 20
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = "appdb"
  username             = "admin"
  password             = "password123"
  skip_final_snapshot  = true
}
