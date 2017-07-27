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

%define debug_package %{nil}

Summary: A utility for getting files from remote servers (FTP, HTTP, and others)
Name: %{pkg_name}
Version: 7.53.1
%define release_prefix 4
Release: %{release_prefix}%{?dist}.cpanel
License: MIT
Vendor: cPanel, Inc.
Group: Applications/Internet
Source: %{pkg_name}-%{version}.tar.gz
URL: http://curl.haxx.se/
BuildRoot: %{_tmppath}/%{pkg_name}-%{version}-%{release}-root

Autoreq: 0
Autoprov: 0

Requires: openssl
Requires: libssh2
Requires: openldap
Requires: krb5-libs
Requires: ea-nghttp2
BuildRequires: ea-openssl
BuildRequires: valgrind
BuildRequires: libidn libidn-devel
BuildRequires: libssh2 libssh2-devel
BuildRequires: openldap openldap-devel
BuildRequires: krb5-devel
BuildRequires: ea-libnghttp2-devel
BuildRequires: ea-openssl-devel
BuildRequires: ea-nghttp2


%description
curl is a client to get documents/files from servers, using any of the
supported protocols. The command is designed to work without user
interaction or any kind of interactivity.

curl offers a busload of useful tricks like proxy support, user
authentication, ftp upload, HTTP post, file transfer resume and more.

%package    devel
Summary:    The includes, libs, and man pages to develop with libcurl
Group:      Development/Libraries
BuildRequires:   ea-openssl-devel

%description devel
libcurl is the core engine of curl; this packages contains all the libs,
headers, and manual pages to develop applications using libcurl.

%prep

%setup -q -n %{pkg_name}-%{version}

%build
cd %{curlroot} && (if [ -f configure.in ]; then mv -f configure.in configure.in.rpm; fi)
LIBS="-ldl"
%configure \
 --with-ssl=/opt/cpanel/ea-openssl \
 --with-libssh2=/usr/local \
 --with-gssapi \
 --enable-tls-srp \
 --enable-ldap \
 --enable-ldaps \
 --enable-unix-sockets \
 --with-nghttp2

cd %{curlroot} && (if [ -f configure.in.rpm ]; then mv -f configure.in.rpm configure.in; fi)
make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
make DESTDIR=%{buildroot} install-strip
install -m 755 -d %{buildroot}%{_defaultdocdir}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
[ "%{curlroot}" != "/" ] && rm -rf %{curlroot}

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

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
%doc docs/TODO docs/VERSIONS docs/TheArtOfHttpScripting tests
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

