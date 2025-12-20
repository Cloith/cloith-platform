resource "null_resource" "vps_clean_setup" {
  # Triggers ensure this re-runs if IP or Password changes
  triggers = {
    vps_ip = var.vps_ip
  }

  connection {
    type     = "ssh"
    user     = "root"
    password = var.vps_password
    host     = var.vps_ip
    timeout  = "5m"
  }

  provisioner "remote-exec" {
    inline = [
      "set -e", # Exit immediately if a command fails

      "echo '--- Phase 1: Installing K3s (NGF Optimized) ---'",
      # Fixed the quoting for INSTALL_K3S_EXEC
      "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='server --disable traefik --disable servicelb' sh -s - --write-kubeconfig-mode 644",

      "echo 'Waiting for K3s to be ready...'",
      "timeout 60 bash -c 'until kubectl get nodes; do sleep 5; done'",

      "echo '--- Phase 2: Installing Gateway API CRDs ---'",
      "kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/standard-install.yaml",

      "echo '--- Phase 3: Installing NGINX Gateway Fabric ---'",
      # Using the edge-case manifest or stable release
      "::",

      "echo '--- Phase 4: Configuring Gateway Resources ---'",
      # This creates both the GatewayClass and the Gateway itself
      <<-EOF
        cat <<INNER | kubectl apply -f -
        apiVersion: gateway.networking.k8s.io/v1
        kind: GatewayClass
        metadata:
          name: nginx
        spec:
          controllerName: gateway.nginx.org/nginx-gateway-controller
        ---
        apiVersion: gateway.networking.k8s.io/v1
        kind: Gateway
        metadata:
          name: nginx-gateway
          namespace: nginx-gateway
        spec:
          gatewayClassName: nginx
          listeners:
          - name: http
            port: 80
            protocol: HTTP
            allowedRoutes:
              namespaces:
                from: All
        INNER
        EOF
    ,
      "echo 'Infrastructure Ready!'"
    ]
  }

  # Pulling the Kubeconfig to your local machine
  provisioner "local-exec" {
    command = <<EOT
      $vpsIp = "${var.vps_ip}"
      scp -o StrictHostKeyChecking=no root@$vpsIp:/etc/rancher/k3s/k3s.yaml ./k3s-vps.yaml
      (Get-Content ./k3s-vps.yaml) -replace '127.0.0.1', $vpsIp | Set-Content ./k3s-vps.yaml
      Write-Host "Kubeconfig downloaded to ./k3s-vps.yaml. Set your KUBECONFIG env var to use it."
    EOT
    interpreter = ["PowerShell", "-Command"]
  }
}