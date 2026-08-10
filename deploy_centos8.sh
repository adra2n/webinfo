#!/bin/bash
# webinfo CentOS 8 部署脚本
# 用法: sudo bash deploy_centos8.sh

set -e

echo "=========================================="
echo "  webinfo 部署脚本 (CentOS 8)"
echo "=========================================="

# 1. 安装系统依赖
echo "[1/6] 安装系统依赖..."
dnf install -y python3 python3-pip nmap wget tar gcc make git

# 2. 安装 Go
echo "[2/6] 安装 Go..."
if ! command -v go &> /dev/null; then
    wget -q https://go.dev/dl/go1.22.5.linux-amd64.tar.gz -O /tmp/go.tar.gz
    tar -C /usr/local -xzf /tmp/go.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile.d/go.sh
    echo 'export GOPATH=$HOME/go' >> /etc/profile.d/go.sh
    echo 'export PATH=$PATH:$GOPATH/bin' >> /etc/profile.d/go.sh
    source /etc/profile.d/go.sh
    rm /tmp/go.tar.gz
    echo "  Go 安装完成: $(go version)"
else
    echo "  Go 已存在: $(go version)"
fi

# 3. 安装 naabu
echo "[3/6] 安装 naabu..."
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

# 4. 安装 pureDNS
echo "[4/6] 安装 pureDNS..."
go install github.com/d3mondev/puredns/v2@latest

# 5. 配置 pureDNS
echo "[5/6] 配置 pureDNS resolvers..."
mkdir -p ~/.config/puredns
cat > ~/.config/puredns/resolvers.txt << 'EOF'
8.8.8.8
8.8.4.4
1.1.1.1
1.0.0.1
9.9.9.9
149.112.112.112
EOF
echo "  resolvers 已配置"

# 6. 安装 Python 依赖
echo "[6/6] 安装 Python 依赖..."
pip3 install --upgrade pip
pip3 install requests beautifulsoup4 lxml IPy python-libnmap openpyxl

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  cd /opt/webinfo"
echo "  sudo python3 shell.py"
echo ""
echo "注意: SYN 扫描需要 root 权限"
