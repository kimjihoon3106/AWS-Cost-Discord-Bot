# AWS-Cost-Discord-Bot

### Install Tools
```
# docker
sudo yum install docker -y
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
sudo chmod 666 /var/run/docker.sock

# docker-compose
sudo mkdir -p /usr/local/lib/docker/cli-plugins/
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version
```

### env
Replace value of DISCORD_WEBHOOK_URL
```
sudo vi .env
```


### Deploy
```
git clone https://github.com/kimjihoon3106/AWS-Cost-Discord-Bot.git
docker build -t aws-cost-bot .
```
```
docker-compose up -d
```
