#!/bin/sh

dir=$PWD
savedir=cards_combined_16
tag0=0x1
tag1=0x0
year=2016
cp -r ttbarfits_cen2016_$tag0 cards_combined_16
#mkdir $dir/$savedir


combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon1000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon1000_area/card.txt > $dir/$savedir/signalRSGluon1000_area/signalRSGluon1000_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon1500_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon1500_area/card.txt > $dir/$savedir/signalRSGluon1500_area/signalRSGluon1500_card.txt


combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon2000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon2000_area/card.txt > $dir/$savedir/signalRSGluon2000_area/signalRSGluon2000_card.txt


combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon2500_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon2500_area/card.txt > $dir/$savedir/signalRSGluon2500_area/signalRSGluon2500_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon3000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon3000_area/card.txt > $dir/$savedir/signalRSGluon3000_area/signalRSGluon3000_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon3500_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon3500_area/card.txt > $dir/$savedir/signalRSGluon3500_area/signalRSGluon3500_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon4000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon4000_area/card.txt > $dir/$savedir/signalRSGluon4000_area/signalRSGluon4000_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon4500_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon4500_area/card.txt > $dir/$savedir/signalRSGluon4500_area/signalRSGluon4500_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon5000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon5000_area/card.txt > $dir/$savedir/signalRSGluon5000_area/signalRSGluon5000_card.txt

combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon5500_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon5500_area/card.txt > $dir/$savedir/signalRSGluon5500_area/signalRSGluon5500_card.txt


combineCards.py Name1=$dir/ttbarfits_cen2016_$tag0/signalRSGluon6000_area/card.txt Name2=$dir/ttbarfits_fwd2016_$tag1/signalRSGluon6000_area/card.txt > $dir/$savedir/signalRSGluon6000_area/signalRSGluon6000_card.txt

echo 'DONE'
echo 'calculating limits'
echo ''

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon1000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon1000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon1000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon1500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon1500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon1500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon2000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon2000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon2000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor



echo "combineTool.py -M AsymptoticLimits -d signalRSGluon2500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon2500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon2500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon3000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon3000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon3000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon3500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon3500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon3500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon4000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon4000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon4000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon4500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon4500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon4500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon5000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon5000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon5000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor

echo "combineTool.py -M AsymptoticLimits -d signalRSGluon5500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon5500_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon5500_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor


echo "combineTool.py -M AsymptoticLimits -d signalRSGluon6000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor"
cd /$dir/$savedir/signalRSGluon6000_area
pwd
combineTool.py -M AsymptoticLimits -d signalRSGluon6000_card.txt --saveWorkspace  --cminDefaultMinimizerStrategy 0 --cminPreScan --cminPreFit 1  --rAbsAcc 0.0001     -v 0 --job-mode condor

cd /$dir



