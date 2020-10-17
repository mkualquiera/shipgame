find "web/" -name "*.js.*" -type f -delete
find "web/" -name "*.js" -type f -delete
tsc -p ./tsconfig.json