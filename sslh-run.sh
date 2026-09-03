#!/bin/bash
# 나스에서 실행: 공인 443 포트 하나로 SSH와 HTTPS를 자동 구분해서 라우팅
# - SSH 트래픽  -> 127.0.0.1:22   (sshd)
# - TLS/HTTPS   -> 127.0.0.1:8443 (docker-compose의 nginx 컨테이너)
#
# 공유기에서는 외부 443 -> 나스 443 하나만 포트포워딩하면 됩니다.

docker run -d \
  --name sslh \
  --restart unless-stopped \
  --network host \
  yrutschle/sslh \
  -f -F /dev/null \
  --listen=0.0.0.0:443 \
  --ssh=127.0.0.1:22 \
  --tls=127.0.0.1:8443