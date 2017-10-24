A server app for iMessage sticker pack app generation
```
[start]

cp -rf __stpapp__ {PATH}/App
cd {PATH}
ios-sticker-pack update
cd App

rna __stp_appname__ stpnewapp
rna __stp_appname_ext__ stpnewapp pack
rna __stp_bundleid__ com.stells.stpnewapp
rna __stp_bundleid_ext__ com.stells.stpnewapp.pack

fastlane init -u croing09@gmail.com
y
fastlane sigh -a com.stells.stpnewapp
fastlane produce -u croing09@gmail.com -q "stpnewapp pack" -a com.stells.stpnewapp.pack --skip_itc
fastlane sigh -a com.stells.stpnewapp.pack
```
