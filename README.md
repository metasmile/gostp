A server app for iMessage sticker pack app generation
```
mkdir gostp_test2
cd gostp_test2
ios-sticker-pack create
cd App
fastlane init
xcodebuild -target gostp_test2 DEVELOPMENT_TEAM=MCAFR355J4 PRODUCT_BUNDLE_IDENTIFIER=com.stells.elie


rename file/text: __stp_appname__ -> appname 
rename file/text: __stp_bundleid__ -> app bundleid
rename file/text: __stp_bundleid_ext__ -> app extension bundleid

fastlane init
fastlane produce -u croing09@gmail.com -a com.stells.stpappid --skip_itc
fastlane produce -u croing09@gmail.com -a com.stells.stpappid.pack --skip_itc
```
