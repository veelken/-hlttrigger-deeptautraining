cd $CMSSW_BASE/src/TauMLTools/Training/python
# CV: use for python 2.7
python _fill_grid_setup.py build
cp $CMSSW_BASE/python/TauMLTools/Training/build/lib.linux-x86_64-2.7/python/fill_grid.so $CMSSW_BASE/python/TauMLTools/Training/
# CV: use for python 3
#python3 _fill_grid_setup.py build
#cp $CMSSW_BASE/python/TauMLTools/Training/build/lib.linux-x86_64-3.8/python/fill_grid.cpython-38-x86_64-linux-gnu.so $CMSSW_BASE/python/TauMLTools/Training/
cd -
