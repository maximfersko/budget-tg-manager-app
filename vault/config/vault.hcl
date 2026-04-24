ui = true
disable_mlock = false

storage "raft" {
  path    = "/vault/data"
  node_id = "vault-node-1"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_disable   = 0

  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file  = "/vault/certs/vault.key"
}

api_addr     = "https://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"