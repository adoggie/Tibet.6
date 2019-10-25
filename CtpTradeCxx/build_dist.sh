rm -f dist
mkdir -p dist/lib
cp cmake-build*/CtpTradeCxx ./dist
cp settings.txt ./dist
cp ctpapi/x64_linux/*.so ./dist
cp  /usr/local/lib/lib*.so dist/lib
#rm -f dist/lib/lib*.so.*

mkdir -p /opt/tibet/ctp/trader
cp -r ./dist/* /opt/tibet/ctp/trader