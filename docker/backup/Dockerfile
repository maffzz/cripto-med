FROM postgres:16-alpine

# Instalar gnupg y bash para cifrado simétrico AES-256 (NIST SP 800-38D / NIST SP 800-57)
RUN apk add --no-cache gnupg bash tzdata

WORKDIR /backups

CMD ["/bin/bash"]
