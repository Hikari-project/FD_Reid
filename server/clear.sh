find ./ -name "*.pyc" | xargs rm -rf
find ./ -name "*.DS_Store" | xargs rm -rf
find ./ -name "__pycache__" | xargs rm -rf
rm -rf ./GUI/outputs
rm -rf ./GUI/config/*