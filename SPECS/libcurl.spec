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
%define ea_openssl_ver 1.0.2n-3
%define ea_nghttp2_ver 1.20.0-7

%define debug_package %{nil}

Summary: A utility for getting files from remote servers (FTP, HTTP, and others)
Name: %{pkg_name}
Version: 7.58.0
%define release_prefix 5
Release: %{release_prefix}%{?dist}.cpanel
License: MIT
Vendor: cPanel, Inc.
Group: Applications/Internet
Source: curl-%{version}.tar.gz
URL: http://curl.haxx.se/
Patch1: 0001-Update-configure-to-allow-additional-LDFLAG-control.patch
BuildRoot: %{_tmppath}/%{pkg_name}-%{version}-%{release}-root

Requires: ea-openssl >= %{ea_openssl_ver}
Requires: krb5-libs
Requires: ea-nghttp2 >= %{ea_nghttp2_ver}
Requires: ea-brotli
BuildRequires: valgrind
BuildRequires: libidn libidn-devel
BuildRequires: krb5-devel
BuildRequires: ea-openssl >= %{ea_openssl_ver}
BuildRequires: ea-openssl-devel >= %{ea_openssl_ver}
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
cd %{curlroot} && (if [ -f configure.in ]; then mv -f configure.in configure.in.rpm; fi)

export LIBS="-ldl"
%configure \
 --with-ssl=/opt/cpanel/ea-openssl \
 --with-ca-bundle=/etc/pki/tls/certs/ca-bundle.crt \
 --with-gssapi \
 --without-nss \
 --enable-tls-srp \
 --enable-unix-sockets \
 --with-nghttp2=/opt/cpanel/nghttp2/ \
 --with-brotli=/opt/cpanel/ea-brotli/ \
 SSL_LDFLAGS="-L/opt/cpanel/ea-openssl/%{_lib} -Wl,-rpath=/opt/cpanel/ea-openssl/%{_lib} " \
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
%doc CHANGES COPYING README docs/BUGS
%doc docs/FAQ docs/FEATURES docs/INSTALL
%doc docs/KNOWN_BUGS docs/MANUAL docs/RESOURCES docs/THANKS
%doc docs/TODO docs/VERSIONS docs/TheArtOfHttpScripting
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

* Tue Nov 29 2017 Cory McIntire <cory@cpanel.net> - 7.57.0-1
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

