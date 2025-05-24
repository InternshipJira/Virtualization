ssh-keygen -t ed25519 -f /app/key -N ''
git clone $GIT_URL
cp /app/*.pub /app/Pub_keys
cd Pub_keys
git add .
git config --global user.name app
git config --global user.email git@github.com
git commit -m '132'
git push
