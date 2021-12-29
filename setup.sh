python3 -m venv venv
source venv/bin/activate
pip3 install wheel
pip3 install jupyter
jupyter nbextension enable vim_binding/vim_binding
git remote rm origin
source venv/bin/activate
