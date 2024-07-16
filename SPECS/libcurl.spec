%define ns_prefix ea
%define pkg_base  libcurl
%define pkg_name  %{ns_prefix}-%{pkg_base}
%define _prefix   /opt/cpanel/%{pkg_base}
%define prefix_dir /opt/cpanel/%{pkg_base}
%define prefix_lib %{prefix_dir}/%{_lib}
%define prefix_bin %{prefix_dir}/bin
%define prefix_inc %{prefix_dir}/include
%define _unpackaged_files_terminate_build 0
%define _defaultdocdir %{_prefix}/share/doc
%define ea_openssl_ver 1.1.1d-1
%define ea_nghttp2_ver 1.51.0-2

Summary: A utility for getting files from remote servers (FTP, HTTP, and others)
Name: %{pkg_name}
Version: 8.8.0
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
License: MIT
Vendor: cPanel, Inc.
Group: Applications/Internet
Source: curl-%{version}.tar.gz
URL: http://curl.haxx.se/
BuildRoot: %{_tmppath}/%{pkg_name}-%{version}-%{release}-root

# ***NOTE*** This patch is 'built with' the 0001 & 0002 patches.
# The 0001 (configure.ac) patche in SOURCES are not used directly during the RPM build process,
# it is used for building the 0002 patch itself whenever a newer version of curl is released.
# General process here is:
#
# 1. Download/extract latest version of curl, and initial a git repo there as so:
#   1a. git init .
#   1b. git add .
#   1c. git commit -m "init"
# 2. Create a patches branch, and apply the 0001 patche to the extracted content as so:
#   2a. git checkout -b "patches"
#   2b. git am </path/to/0001patch>
# 3. Run "autoconf" to update the configure file, and then commit the updated file to the patches branch:
#   3a. git add configure
#   3b. git commit
# 4. Build the final patch files with:
#   4a. git format-patch --zero-commit --no-signature master..patches
Patch1: 0002-Rebuild-configure-with-the-additional-LDFLAG-for-Bro.patch

%if 0%{?rhel} < 7
Requires: libssh2 >= 1.4.2
%else
Requires: libssh2 >= 1.8.0
%endif
%if 0%{?rhel} < 8
Requires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11-devel >= %{ea_openssl_ver}
%if 0%{?rhel} < 7
BuildRequires: devtoolset-7-toolchain
BuildRequires: devtoolset-7-libatomic-devel
BuildRequires: devtoolset-7-gcc
BuildRequires: devtoolset-7-gcc-c++
%else
BuildRequires: devtoolset-8-toolchain
BuildRequires: devtoolset-8-libatomic-devel
BuildRequires: devtoolset-8-gcc
BuildRequires: devtoolset-8-gcc-c++
%endif
%else
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
Requires: openssl
BuildRequires: openssl
BuildRequires: openssl
%endif

Requires: krb5-libs
Requires: ea-nghttp2 >= %{ea_nghttp2_ver}
Requires: ea-brotli
BuildRequires: valgrind
BuildRequires: libidn libidn-devel
BuildRequires: libssh2 libssh2-devel
BuildRequires: krb5-devel
BuildRequires: ea-libnghttp2 >= %{ea_nghttp2_ver}
BuildRequires: ea-libnghttp2-devel >= %{ea_nghttp2_ver}
BuildRequires: ea-brotli, ea-brotli-devel

%description
curl is a client to get documents/files from servers, using any of the
supported protocols. The command is designed to work without user
interaction or any kind of interactivity.

curl offers a busload of useful tricks like proxy support, user
authentication, ftp upload, HTTP post, file transfer resume and more.

%package    devel
Summary:    The includes, libs, and man pages to develop with libcurl
Group:      Development/Libraries

%description devel
libcurl is the core engine of curl; this packages contains all the libs,
headers, and manual pages to develop applications using libcurl.

%prep

%setup -q -n curl-%{version}
%patch1 -p1 -b .sslldflags

%build
%if 0%{?rhel} < 8
%if 0%{?rhel} < 7
. /opt/rh/devtoolset-7/enable
%else
. /opt/rh/devtoolset-8/enable
%endif
%endif
cd %{curlroot} && (if [ -f configure.in ]; then mv -f configure.in configure.in.rpm; fi)

export LIBS="-ldl"
%configure \
%if 0%{?rhel} < 8
 --with-openssl=/opt/cpanel/ea-openssl11 \
%else
 --with-openssl \
%endif
 --with-ca-bundle=/etc/pki/tls/certs/ca-bundle.crt \
 --with-libssh2=/usr/local \
 --with-gssapi \
 --without-nss \
 --enable-tls-srp \
 --enable-unix-sockets \
 --with-nghttp2=/opt/cpanel/nghttp2/ \
 --with-brotli=/opt/cpanel/ea-brotli/ \
 --without-libpsl \
%if 0%{?rhel} < 8
 SSL_LDFLAGS="-L/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib} " \
%endif
 LD_H2="-L/opt/cpanel/nghttp2/lib -Wl,-rpath=/opt/cpanel/nghttp2/lib " \
 LD_BROTLI="-L/opt/cpanel/ea-brotli/lib -Wl,-rpath=/opt/cpanel/ea-brotli/lib "

cd %{curlroot} && (if [ -f configure.in.rpm ]; then mv -f configure.in.rpm configure.in; fi)
make

# We dont run tests, so just get rid of the directory for now.
rm -rf tests

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
make DESTDIR=%{buildroot} install-strip
install -m 755 -d %{buildroot}%{_defaultdocdir}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
[ "%{curlroot}" != "/" ] && rm -rf %{curlroot}

%files -n %{pkg_name}
%defattr(-,root,root,-)
%attr(0755,root,root) %{_bindir}/curl
%{_libdir}/libcurl.so*
%dir %{_prefix}
%dir %{_prefix}/share
%dir %{_libdir}
%dir %{prefix_bin}
%dir %{prefix_inc}
%dir %{prefix_lib}
%doc CHANGES COPYING README
%doc docs/FAQ docs/FEATURES.md docs/INSTALL
%doc docs/KNOWN_BUGS docs/THANKS
%doc docs/TODO docs/VERSIONS.md
%dir %{_defaultdocdir}

%files -n %{pkg_name}-devel
%defattr(-,root,root,-)
%attr(0755,root,root) %{_bindir}/curl-config
%attr(0644,root,root) %{_includedir}/curl/*
%dir %{_prefix}
%dir %{_libdir}
%dir %{_includedir}
%dir %{prefix_dir}/include/curl
%dir %{prefix_bin}
%dir %{prefix_inc}
%dir %{prefix_lib}
%{_libdir}/libcurl.a
%{_libdir}/libcurl.la
%doc docs/examples/*
%dir %{_defaultdocdir}

%changelog
* Thu Jun 13 2024 Cory McIntire <cory@cpanel.net> - 8.8.0-1
- EA-12212: Update libcurl from v8.7.1 to v8.8.0

* Mon Apr 15 2024 Cory McIntire <cory@cpanel.net> - 8.7.1-2
- EA-12080: patch update that caused issues with CURLOPT_ACCEPT_ENCODING

* Wed Mar 27 2024 Cory McIntire <cory@cpanel.net> - 8.7.1-1
- EA-12051: Update libcurl from v8.6.0 to v8.7.1
- CVE-2024-2466: TLS certificate check bypass with mbedTLS
- CVE-2024-2398: HTTP/2 push headers memory-leak
- CVE-2024-2379: QUIC certificate check bypass with wolfSSL
- CVE-2024-2004: Usage of disabled protocol

* Mon Feb 05 2024 Cory McIntire <cory@cpanel.net> - 8.6.0-1
- EA-11948: Update libcurl from v8.5.0 to v8.6.0
- CVE-2024-0853: OCSP verification bypass with TLS session reuse

* Wed Dec 06 2023 Cory McIntire <cory@cpanel.net> - 8.5.0-1
- EA-11857: Update libcurl from v8.4.0 to v8.5.0
- CVE-2023-46219 - HSTS long file name clears contents
- CVE-2023-46218 - cookie mixed case PSL bypass

* Wed Oct 11 2023 Cory McIntire <cory@cpanel.net> - 8.4.0-1
- EA-11731: Update libcurl from v8.3.0 to v8.4.0
- CVE-2023-38545 - SOCKS5 heap buffer overflow
- CVE-2023-38546 - cookie injection with none file

* Wed Sep 13 2023 Cory McIntire <cory@cpanel.net> - 8.3.0-1
- EA-11680: Update libcurl from v8.2.1 to v8.3.0
- CVE-2023-38039: HTTP headers eat all memory

* Fri Jul 28 2023 Cory McIntire <cory@cpanel.net> - 8.2.1-1
- EA-11574: Update libcurl from v8.2.0 to v8.2.1

* Wed Jul 19 2023 Cory McIntire <cory@cpanel.net> - 8.2.0-1
- EA-11560: Update libcurl from v8.1.2 to v8.2.0
- CVE-2023-32001 curl: fopen race condition

* Tue May 30 2023 Cory McIntire <cory@cpanel.net> - 8.1.2-1
- EA-11448: Update libcurl from v8.1.1 to v8.1.2

* Tue May 23 2023 Cory McIntire <cory@cpanel.net> - 8.1.1-1
- EA-11432: Update libcurl from v8.0.1 to v8.1.1
   - CVE-2023-28322: more POST-after-PUT confusion
   - CVE-2023-28321: IDN wildcard match
   - CVE-2023-28320: siglongjmp race condition
   - CVE-2023-28319: UAF in SSH sha256 fingerprint check

* Tue May 09 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 8.0.1-2
- ZC-10936: Clean up Makefile and remove debug-package-nil

* Mon Mar 20 2023 Cory McIntire <cory@cpanel.net> - 8.0.1-1
- EA-11303: Update libcurl from v7.88.1 to v8.0.1
- CVE-2023-27538: SSH connection too eager reuse still
- CVE-2023-27537: HSTS double-free
= CVE-2023-27536: GSS delegation too eager connection re-use
= CVE-2023-27535: FTP too eager connection reuse
- CVE-2023-27534: SFTP path ~ resolving discrepancy

* Mon Feb 20 2023 Cory McIntire <cory@cpanel.net> - 7.88.1-1
- EA-11256: Update libcurl from v7.88.0 to v7.88.1

* Wed Feb 15 2023 Cory McIntire <cory@cpanel.net> - 7.88.0-1
- EA-11241: Update libcurl from v7.87.0 to v7.88.0
- CVE-2023-23916: HTTP multi-header compression denial of service
- CVE-2023-23915: HSTS amnesia with --parallel
- CVE-2023-23914: HSTS ignored on multiple requests

* Wed Feb 08 2023 Travis Holloway <t.holloway@cpanel.net> - 7.87.0-2
- EA-11221: Bump minimum required nghttp2 version to 1.51.0-2

* Wed Dec 21 2022 Cory McIntire <cory@cpanel.net> - 7.87.0-1
- EA-11118: Update libcurl from v7.86.0 to v7.87.0
- CVE-2022-43551: Another HSTS bypass via IDN
- CVE-2022-43552: HTTP Proxy deny use-after-free

* Thu Oct 27 2022 Cory McIntire <cory@cpanel.net> - 7.86.0-1
- EA-11016: Update libcurl from v7.85.0 to v7.86.0
- CVE-2022-32221: POST following PUT confusion
- CVE-2022-35260: .netrc parser out-of-bounds access
- CVE-2022-42915: HTTP proxy double-free
- CVE-2022-42916: HSTS bypass via IDN

* Wed Aug 31 2022 Cory McIntire <cory@cpanel.net> - 7.85.0-1
- EA-10914: Update libcurl from v7.84.0 to v7.85.0

* Mon Jun 27 2022 Cory McIntire <cory@cpanel.net> - 7.84.0-1
- EA-10790: Update libcurl from v7.83.1 to v7.84.0
- CVE-2022-32208: FTP-KRB bad message verification
- CVE-2022-32207: Unpreserved file permissions
- CVE-2022-32206: HTTP compression denial of service
- CVE-2022-32205: Set-Cookie denial of service

* Wed May 11 2022 Cory McIntire <cory@cpanel.net> - 7.83.1-1
- EA-10702: Update libcurl from v7.83.0 to v7.83.1

* Wed Apr 27 2022 Cory McIntire <cory@cpanel.net> - 7.83.0-1
- EA-10666: Update libcurl from v7.82.0 to v7.83.0

* Mon Mar 07 2022 Travis Holloway <t.holloway@cpanel.net> - 7.82.0-1
- EA-10537: Update libcurl from v7.81.0 to v7.82.0

* Wed Jan 05 2022 Cory McIntire <cory@cpanel.net> - 7.81.0-1
- EA-10408: Update libcurl from v7.80.0 to v7.81.0

* Tue Dec 28 2021 Dan Muey <dan@cpanel.net> - 7.80.0-2
- ZC-9589: Update DISABLE_BUILD to match OBS

* Thu Nov 11 2021 Tim Mullin <tim@cpanel.net> - 7.80.0-1
- EA-10274: Update libcurl from v7.79.1 to v7.80.0

* Fri Sep 24 2021 Cory McIntire <cory@cpanel.net> - 7.79.1-1
- EA-10135: Update libcurl from v7.79.0 to v7.79.1

* Thu Sep 16 2021 Cory McIntire <cory@cpanel.net> - 7.79.0-1
- EA-10110: Update libcurl from v7.78.0 to v7.79.0

* Thu Jul 22 2021 Cory McIntire <cory@cpanel.net> - 7.78.0-1
- EA-9982: Update libcurl from v7.77.0 to v7.78.0

* Tue Jun 01 2021 Tim Mullin <tim@cpanel.net> - 7.77.0-2
- EA-9816: Fix linking to openssl

* Wed May 26 2021 Tim Mullin <tim@cpanel.net> - 7.77.0-1
- EA-9794: Update libcurl from v7.76.1 to v7.77.0

* Fri Apr 23 2021 Cory McIntire <cory@cpanel.net> - 7.76.1-1
- EA-9710: Update libcurl from v7.76.0 to v7.76.1

* Tue Apr 06 2021 Cory McIntire <cory@cpanel.net> - 7.76.0-1
- EA-9677: Update libcurl from v7.75.0 to v7.76.0

* Thu Feb 04 2021 Cory McIntire <cory@cpanel.net> - 7.75.0-1
- EA-9567: Update libcurl from v7.74.0 to v7.75.0

* Thu Dec 10 2020 Cory McIntire <cory@cpanel.net> - 7.74.0-1
- EA-9479: Update libcurl from v7.73.0 to v7.74.0

* Tue Nov 24 2020 Julian Brown <julian.brown@cpanel.net> - 7.73.0-2
- ZC-8005: Replace ea-openssl11 with system openssl on C8

* Wed Oct 14 2020 Cory McIntire <cory@cpanel.net> - 7.73.0-1
- EA-9371: Update libcurl from v7.72.0 to v7.73.0

* Wed Aug 19 2020 Cory McIntire <cory@cpanel.net> - 7.72.0-1
- EA-9260: Update libcurl from v7.71.1 to v7.72.0

* Mon Jul 06 2020 Cory McIntire <cory@cpanel.net> - 7.71.1-1
- EA-9138: Update libcurl from v7.71.0 to v7.71.1

* Wed Jun 24 2020 Cory McIntire <cory@cpanel.net> - 7.71.0-1
- EA-9124: Update libcurl from v7.70.0 to v7.71.0

* Wed Apr 29 2020 Cory McIntire <cory@cpanel.net> - 7.70.0-1
- EA-9044: Update libcurl from v7.69.1 to v7.70.0

* Tue Mar 31 2020 Tim Mullin <tim@cpanel.net> - 7.69.1-2
- EA-8928: Added version check for libssh2

* Fri Mar 27 2020 Cory McIntire <cory@cpanel.net> - 7.69.1-1
- EA-8947: Update libcurl from v7.68.0 to v7.69.1

* Fri Feb 07 2020 Tim Mullin <tim@cpanel.net> - 7.68.0-1
- EA-8843: Update libcurl from v7.67.0 to v7.68.0

* Wed Dec 18 2019 Danie Muey <dan@cpanel.net> - 7.67.0-3
- ZC-4361: Update ea-openssl requirement to v1.1.1 (ZC-5583)

* Thu Nov 21 2019 Tim Mullin <tim@cpanel.net> - 7.67.0-2
- EA-8754: Patch libcurl 7.67.0 for OpenSSL issue breaking WHMCS

* Fri Nov 08 2019 Cory McIntire <cory@cpanel.net> - 7.67.0-1
- EA-8739: Update libcurl from v7.66.0 to v7.67.0

* Wed Sep 11 2019 Cory McIntire <cory@cpanel.net> - 7.66.0-1
- EA-8649: Update libcurl from v7.65.3 to v7.66.0

* Mon Jul 22 2019 Cory McIntire <cory@cpanel.net> - 7.65.3-1
- EA-8584: Update libcurl from v7.65.1 to v7.65.3

* Thu Jun 27 2019 Cory McIntire <cory@cpanel.net> - 7.65.1-1
- EA-8546: Update libcurl from v7.65.0 to v7.65.1

* Wed May 22 2019 Cory McIntire <cory@cpanel.net> - 7.65.0-1
- EA-8475: Update libcurl from v7.64.1 to v7.65.0

* Thu May 16 2019 Cory McIntire <cory@cpanel.net> - 7.64.1-1
- EA-8472: Update libcurl from v7.64.0 to v7.64.1

* Wed Apr 03 2019 Tim Mullin <tim@cpanel.net> - 7.64.0-2
EA-8303: Removed libssh2-devel as a dependency; this caused problems for RHEL

* Thu Feb 07 2019 Cory McIntire <cory@cpanel.net> - 7.64.0-1
- EA-8204: Update cURL from 7.63.0 to 7.64.0
  https://curl.haxx.se/docs/CVE-2018-16890.html
  https://curl.haxx.se/docs/CVE-2019-3822.html
  https://curl.haxx.se/docs/CVE-2019-3823.html

* Tue Jan 29 2019 Tim Mullin <tim@cpanel.net> - 7.63.0-1
- EA-8187: Update cURL from 7.62.0 to 7.63.0

* Tue Nov 06 2018 Tim Mullin <tim@cpanel.net> - 7.62.0-2
- EA-7983: Added libssh2-devel as a dependency

* Thu Nov 01 2018 Cory McIntire <cory@cpanel.net> - 7.62.0-1
- EA-7978: Update cURL from 7.61.1 to 7.62.0 for CVEs
  https://curl.haxx.se/docs/CVE-2018-16839.html
  https://curl.haxx.se/docs/CVE-2018-16840.html
  https://curl.haxx.se/docs/CVE-2018-16842.html

* Mon Oct 01 2018 Cory McIntire <cory@cpanel.net> - 7.61.1-1
- EA-7819: Update cURL from 7.61.0 to 7.61.1
- CVE-2018-14618 https://curl.haxx.se/docs/CVE-2018-14618.html
- Low priority CVE, 32 bit systems only

* Thu Jul 12 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.61.0-1
- EA-7654: Update cURL from 7.60.0 to 7.61.0
- CVE-2018-0500 https://curl.haxx.se/docs/adv_2018-70a2.html

* Wed May 16 2018 Cory McIntire <cory@cpanel.net> - 7.60.0-1
- ZC-3769: Update cURL from 7.59.0 to 7.60.0
- CVE-2018-1000300 https://curl.haxx.se/docs/adv_2018-82c2.html

* Mon Apr 16 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.59.0-2
- EA-7382: Update dependency on ea-openssl to require the latest version with versioned symbols.
- ZC-3626: Re-enable SFTP support via libssh2.

* Sun Apr 01 2018 Cory McIntire <cory@cpanel.net> - 7.59.0-1
- EA-7336: Update cURL from 7.58.0 to 7.59.0

* Mon Mar 26 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.58.0-5
- ZC-3552: Ensure curl is linked again ea-openssl, and ea-nghttp2
  Additionally, added support for brotli.
  Added versioning to ea-openssl and nghttp2 requirements for easier
  maintenance.

* Wed Mar 07 2018 Cory McIntire <cory@cpanel.net> - 7.58.0-4
- ZC-3479: Ensure we only link only against our ea-openssl

* Thu Feb 08 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.58.0-3
- EA-7233: Require the newer version of ea-nghttp2 to ensure that
  the packages are updated as a set.

* Wed Feb 07 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.58.0-2
- EA-7219: Build curl against the ea-nghttp2 that is installed
  in /opt/cpanel/nghttp2 to ensure that http2 can still be utilized.

* Wed Jan 24 2018 Dan Muey <dan@cpanel.net> - 7.58.0-1
- EA-7157: Update cURL to 7.58.0

* Wed Nov 29 2017 Cory McIntire <cory@cpanel.net> - 7.57.0-1
- EA-6989: Update cURL to 7.57.0 to deal with CVE
- CVE-2017-8816, CVE-2017-8817, CVE-2017-8818

* Tue Aug 15 2017 Cory McIntire <cory@cpanel.net> - 7.55.1-2
- Bringing in ea-openssl as a Requires to fix EA-6671

* Mon Aug 14 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.55.1-1
- Updated to cURL 7.55.1

* Fri Jul 28 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.53.1-5
- Fix export for static OpenSSL libraries

* Thu Jul 27 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.53.1-4
- Added ALPN support

* Fri Jun 09 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.53.1-3
- Add HTTP2 support

* Mon Apr 03 2017 Cory McIntire <cory@cpanel.net> - 7.53.1-2
- Updated the package with changes suggested by @ezamriy (Eugene Zamriy)
- https://github.com/CpanelInc/libcurl/pull/1
- Removed unnecessary ea-libcurl and ea-libcurl-devel Provides
- Removed incorrect valgrind and perl* Provides workaround
- Disable automatic Requires generation to avoid broken dependencies
- Disable automatic Provides generation to avoid conflicts with system curl
- Added libssh2, openldap, krb5-libs requirements
- Added krb5-devel build requirement

* Mon Mar 13 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.53.1-1
- Updated to 7.53.1

* Tue Mar 07 2017 Cory McIntire <cory@cpanel.net> - 7.38.0-4
- Removed leftover c-ares build requires

* Thu Mar 02 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.38.0-3
- Removed AsynchDNS feature as it isn't required at this time

* Tue Feb 28 2017 Cory McIntire <cory@cpanel.net> - 7.38.0-2
- ZC-2452: Fix missing Available protocols and features

* Fri Feb 17 2017 Cory McIntire <cory@cpanel.net> - 7.38.0-1
- ZC-2421: Create libcurl package

