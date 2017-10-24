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

>> Fastfile write to head.
  produce(username:"croing09@gmail.com", app_name:"stpnewapp", app_identifier:"com.stells.stpnewapp", skip_itc:true)
  produce(username:"croing09@gmail.com", app_name:"stpnewapp pack", app_identifier:"com.stells.stpnewapp.pack", skip_itc:true)
  sigh(app_identifier:"com.stells.stpnewapp")
  sigh(app_identifier:"com.stells.stpnewapp.pack")
  update_project_provisioning(xcodeproj:"stpnewapp.xcodeproj",profile: "./AppStore_com.stells.stpnewapp.mobileprovision", target_filter:"stpnewapp", build_configuration: "Release")
  update_project_provisioning(xcodeproj:"stpnewapp.xcodeproj",profile: "./AppStore_com.stells.stpnewapp.pack.mobileprovision", target_filter:"StickerPackExtension", build_configuration: "Release")

```
