FROM nginx:1.27-alpine

# Copy built React application
COPY dist/ /usr/share/nginx/html/

# Create nginx configuration for API proxy
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /api/ { \
        proxy_pass http://social_network_backend:5000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        \
        add_header Access-Control-Allow-Origin * always; \
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always; \
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always; \
        \
        if ($request_method = "OPTIONS") { \
            add_header Access-Control-Allow-Origin *; \
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"; \
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization"; \
            add_header Access-Control-Max-Age 1728000; \
            add_header Content-Type "text/plain; charset=utf-8"; \
            add_header Content-Length 0; \
            return 204; \
        } \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
