@echo off
chcp 65001 >nul
set "PATH=C:\Program Files\Git\bin;%PATH%"

git init
git config user.name "DailyBetterBot"
git config user.email "bot@dailybetter.com"
git add .
git commit -m "feat: Initial commit - Daily Better AI Blog"
echo DONE!
