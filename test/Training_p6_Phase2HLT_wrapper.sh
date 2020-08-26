cd $CMSSW_BASE/src/TauMLTools/Training/python/Phase2HLTv2
echo "executing command = 'Training_p6_Phase2HLT.py --input $1 --model $2'"
python Training_p6_Phase2HLT.py --input $1 --model $2
cd -
