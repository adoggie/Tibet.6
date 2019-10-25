

MANTIS_PATH=/home/samba/data/Porjects/Branches/mantis
#MANTIS_PATH=/home/scott/projects/mantis

# cmake version >=13.
#CMAKE=/home/scott/Downloads/clion-2018.3.3/bin/cmake/linux/bin/cmake
CMAKE=cmake3

pwd=$(cd `dirname $0`;pwd)
DIST_DIR=$pwd/../dist

#DIST_DIR=/opt

rm -rf $DIST_DIR/*


CTP_TRADE_DIR=$DIST_DIR/tibet/trader
mkdir -p $CTP_TRADE_DIR

cd ../CtpTradeCxx
mkdir build-simnow; cd build-simnow ; rm -rf *
$CMAKE ../ -Dsimnow=ON -Dzsqh_test=OFF -Dzsqh_prd=OFF ; make
cp CtpTrade-simnow $CTP_TRADE_DIR/

cd ../
mkdir build-zsqh-test; cd build-zsqh-test ; rm -rf *
$CMAKE ../ -Dsimnow=OFF -Dzsqh_test=ON -Dzsqh_prd=OFF ; make
cp CtpTrade-zsqh-test $CTP_TRADE_DIR/

cd ../
mkdir build-zsqh-prd; cd build-zsqh-prd ; rm -rf *
$CMAKE ../ -Dsimnow=OFF -Dzsqh_test=OFF -Dzsqh_prd=ON ; make
cp CtpTrade-zsqh-prd $CTP_TRADE_DIR/

cp ../settings.txt $CTP_TRADE_DIR/


cd $pwd

# ----- market -------

CTP_MARKET_DIR=$DIST_DIR/tibet/market
mkdir -p $CTP_MARKET_DIR
echo `pwd`
cd ../CtpMarketCxx
mkdir build-simnow; cd build-simnow ; rm -rf *
$CMAKE ../ -Dsimnow=ON -Dzsqh_test=OFF -Dzsqh_prd=OFF ; make
cp CtpMarket-simnow $CTP_MARKET_DIR/

cd ../
mkdir build-zsqh-test; cd build-zsqh-test ; rm -rf *
$CMAKE ../ -Dsimnow=OFF -Dzsqh_test=ON -Dzsqh_prd=OFF ; make
cp CtpMarket-zsqh-test $CTP_MARKET_DIR/

cd ../
mkdir build-zsqh-prd; cd build-zsqh-prd ; rm -rf *
$CMAKE ../ -Dsimnow=OFF -Dzsqh_test=OFF -Dzsqh_prd=ON ; make
cp CtpMarket-zsqh-prd $CTP_MARKET_DIR/

cp ../settings.txt $CTP_MARKET_DIR/

cd $pwd

cp $pwd/../CTP/zsqh/*.txt $CTP_MARKET_DIR
cp $pwd/../CTP/zsqh/*.txt $CTP_TRADE_DIR

# ----- genius bar maker -------

GENIUSBAR_DIR=$DIST_DIR/tibet/geniusbar

mkdir -p $GENIUSBAR_DIR
cp -r ../GeniusBarMaker/* $GENIUSBAR_DIR

# --- .so ---

mkdir -p $DIST_DIR/tibet/lib
cp  /usr/local/lib/lib*.so $DIST_DIR/tibet/lib

# --- mantis ---
mkdir -p $DIST_DIR/tibet/pythonpath/mantis
cp -r $MANTIS_PATH/fundamental $DIST_DIR/tibet/pythonpath/mantis
cp -r $MANTIS_PATH/sg $DIST_DIR/tibet/pythonpath/mantis/sg
cp -r $MANTIS_PATH/trade $DIST_DIR/tibet/pythonpath/mantis/trade
touch $MANTIS_PATH/trade $DIST_DIR/tibet/pythonpath/mantis/__init__.py

# -- market data recorder
cp -r ../CtpMarketDataRecorder $DIST_DIR/tibet/datarecorder


cp start_server.sh  $DIST_DIR/tibet
cp stop_server.sh  $DIST_DIR/tibet

