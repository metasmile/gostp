A server app for iMessage sticker pack app generation

mkdir gostp_test2
cd gostp_test2
ios-sticker-pack create
cd App
fastlane init
xcodebuild -target gostp_test2 DEVELOPMENT_TEAM=MCAFR355J4 PRODUCT_BUNDLE_IDENTIFIER=com.stells.elie
