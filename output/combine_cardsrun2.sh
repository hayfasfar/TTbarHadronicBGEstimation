#!/bin/sh

dir=/afs/cern.ch/work/h/hrejebsf/private/backgroundEstimate/CMSSW_10_6_14/src/BE_LTM/results
savedir=cards_combined_run2 
mkdir $dir/$savedir

combineCards.py Name1=$dir/cards_combined_16/signalRSGluon1000_area/signalRSGluon1000_card.txt Name2=$dir/cards_combined_17/signalRSGluon1000_area/signalRSGluon1000_card.txt Name3=$dir/cards_combined_18/signalRSGluon1000_area/signalRSGluon1000_card.txt > $dir/$savedir/signalRSGluon1000_area/signalRSGluon1000_card_combined.txt



combineCards.py Name1=$dir/cards_combined_16/signalRSGluon1500_area/signalRSGluon1500_card.txt Name2=$dir/cards_combined_17/signalRSGluon1500_area/signalRSGluon1500_card.txt Name3=$dir/cards_combined_18/signalRSGluon1500_area/signalRSGluon1500_card.txt > $dir/$savedir/signalRSGluon1500_area/signalRSGluon1500_card_combined.txt


combineCards.py Name1=$dir/cards_combined_16/signalRSGluon2000_area/signalRSGluon2000_card.txt Name2=$dir/cards_combined_17/signalRSGluon2000_area/signalRSGluon2000_card.txt Name3=$dir/cards_combined_18/signalRSGluon2000_area/signalRSGluon2000_card.txt > $dir/$savedir/signalRSGluon2000_area/signalRSGluon2000_card_combined.txt


combineCards.py Name1=$dir/cards_combined_16/signalRSGluon2500_area/signalRSGluon2500_card.txt Name2=$dir/cards_combined_17/signalRSGluon2500_area/signalRSGluon2500_card.txt Name3=$dir/cards_combined_18/signalRSGluon2500_area/signalRSGluon2500_card.txt > $dir/$savedir/signalRSGluon2500_area/signalRSGluon2500_card_combined.txt


combineCards.py Name1=$dir/cards_combined_16/signalRSGluon3000_area/signalRSGluon3000_card.txt Name2=$dir/cards_combined_17/signalRSGluon3000_area/signalRSGluon3000_card.txt Name3=$dir/cards_combined_18/signalRSGluon3000_area/signalRSGluon3000_card.txt > $dir/$savedir/signalRSGluon3000_area/signalRSGluon3000_card_combined.txt

combineCards.py Name1=$dir/cards_combined_16/signalRSGluon3500_area/signalRSGluon3500_card.txt Name2=$dir/cards_combined_17/signalRSGluon3500_area/signalRSGluon3500_card.txt Name3=$dir/cards_combined_18/signalRSGluon3500_area/signalRSGluon3500_card.txt > $dir/$savedir/signalRSGluon3500_area/signalRSGluon3500_card_combined.txt


combineCards.py Name1=$dir/cards_combined_16/signalRSGluon4000_area/signalRSGluon4000_card.txt Name2=$dir/cards_combined_17/signalRSGluon4000_area/signalRSGluon4000_card.txt Name3=$dir/cards_combined_18/signalRSGluon4000_area/signalRSGluon4000_card.txt > $dir/$savedir/signalRSGluon4000_area/signalRSGluon4000_card_combined.txt


combineCards.py Name1=$dir/cards_combined_16/signalRSGluon4500_area/signalRSGluon4500_card.txt Name2=$dir/cards_combined_17/signalRSGluon4500_area/signalRSGluon4500_card.txt Name3=$dir/cards_combined_18/signalRSGluon4500_area/signalRSGluon4500_card.txt > $dir/$savedir/signalRSGluon4500_area/signalRSGluon4500_card_combined.txt

combineCards.py Name1=$dir/cards_combined_16/signalRSGluon5000_area/signalRSGluon5000_card.txt Name2=$dir/cards_combined_17/signalRSGluon5000_area/signalRSGluon5000_card.txt Name3=$dir/cards_combined_18/signalRSGluon5000_area/signalRSGluon5000_card.txt > $dir/$savedir/signalRSGluon5000_area/signalRSGluon5000_card_combined.txt

combineCards.py Name1=$dir/cards_combined_16/signalRSGluon5500_area/signalRSGluon5500_card.txt Name2=$dir/cards_combined_17/signalRSGluon5500_area/signalRSGluon5500_card.txt Name3=$dir/cards_combined_18/signalRSGluon5500_area/signalRSGluon5500_card.txt > $dir/$savedir/signalRSGluon5500_area/signalRSGluon5500_card_combined.txt

combineCards.py Name1=$dir/cards_combined_16/signalRSGluon6000_area/signalRSGluon6000_card.txt Name2=$dir/cards_combined_17/signalRSGluon6000_area/signalRSGluon6000_card.txt Name3=$dir/cards_combined_18/signalRSGluon6000_area/signalRSGluon6000_card.txt > $dir/$savedir/signalRSGluon6000_area/signalRSGluon6000_card_combined.txt

echo 'DONE'
echo 'calculating limits'
echo ''

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon1000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon1000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon1000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon1500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon1500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon1500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon2000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon2000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon2000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor



echo "combineTool.py -M AsymptoticLimits -d signalRSGluon2500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon2500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon2500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon3000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon3000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon3000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon3500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon3500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon3500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon4000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon4000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon4000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon4500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon4500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon4500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon5000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon5000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon5000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon5500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon5500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon5500_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor
cd /$dir

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon6000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon6000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon6000_card_combined.txt --saveWorkspace --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1 --rAbsAcc 0.0001   -v 0 --job-mode condor


