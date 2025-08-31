
resource "vault_policy" "app" {
  name = "app-policy"
  policy = <<EOT
path "secret/data/*" {
  capabilities = ["read"]
}
EOT
}
