# iOS project configuration
This is the `src` path to the XCode project of the **P2PSP for iOS** app. To compile the XCode project we need to include several libraries as **Boost**, **VLCKit** and **OpenSSL** into `p2psp/src/ios/lib`.

#### VLCKit
- You can download the compiled version of VLCKit for iOS [here](http://nightlies.videolan.org/build/ios/) and extract it to the `lib` directory mentioned above.

#### Boost
- To compile **Boost** for iOS you can clone wherever you want the following repository https://github.com/danoli3/ofxiOSBoost.
- Edit the file `ofxiOSBoost/scripts/build-libc++` and change `BOOST_LIBS` with the required libraries to our P2PSP project: `${BOOST_LIBS:="system thread program_options log"}` so we don't let the boost binary file be really large.
- Then just run the script and be patient. It takes a long time to finish.
- When the compilation is finished, place `libboost.a` into `p2psp/src/ios/lib/ios/libboost.a`, and the boost headers to `p2psp/src/ios/lib/include/boost`

#### OpenSSL
- There are some functions in some common source files in the `core` that make use of OpenSSL headers, but currently those functions are not being called yet because that functionality is still under develpment. So, to avoid compiling OpenSSL for iOS, we just need to add a symlink to our `openssl` root into `p2psp/src/ios/lib`.
- You can install openssl using [brew](http://brew.sh/).
- Then run `brew install openssl`.
- Go to `p2psp/src/ios/lib` and run `ln -s /usr/local/Cellar/openssl/[your_version]/ openssl`

Then you can open the project file in `p2psp/src/ios/p2psp-ios/p2psp-ios.xcodeproj` with **XCode 7** (or above) and run it.
