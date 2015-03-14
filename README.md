# android的应用自动签名、发布服务端
服务端基于django app。可以通过网页或者[apkauto](https://github.com/rayer4u/apkauto)工具进行上传未签名的apk包。网页上传依赖[progressbarupload](https://github.com/rayer4u/django-progressbarupload)项目用来显示进度。

服务器签名依赖[jdk](http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html)

使用*zipalign*可执行文件进行对齐，可以在[android sdk]包(http:://developer.android.com/sdk/)里获得，centos需要安装以下库才能正常运行  
`yum install glibc.i686 zlib.i686 libstdc++.so.6 `

**暂时内部使用，无配置项**
