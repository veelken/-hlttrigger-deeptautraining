cd $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2
echo "executing command = 'python SplitNetwork_Phase2HLT.py --input $1 --model $2'"
python SplitNetwork_Phase2HLT.py --input $1 --model $2
cd -
