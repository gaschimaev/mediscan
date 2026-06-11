# Menggunakan web server Nginx yang sangat ringan
FROM nginx:alpine

# Menghapus halaman bawaan Nginx
RUN rm -rf /usr/share/nginx/html/*

# Menyalin file index.html buatan teman Anda ke dalam mesin web server
COPY . /usr/share/nginx/html

# Membuka port 80 ke publik
EXPOSE 80

# Menyalakan Nginx terus-menerus
CMD ["nginx", "-g", "daemon off;"]
