
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?pecl_phpdir: %{expand: %%global pecl_phpdir  %(%{__pecl} config-get php_dir  2> /dev/null || echo undefined)}}
%{?!pecl_xmldir: %{expand: %%global pecl_xmldir %{pecl_phpdir}/.pkgxml}}

%define php_extdir %(php-config --extension-dir 2>/dev/null || echo %{_libdir}/php4)                     
%global php_zendabiver %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP Extension => //p') | tail -1)
%global php_version %((echo 0; php-config --version 2>/dev/null) | tail -1)
%define pecl_name APC
%{?!_without_php_ver_tag: %define php_ver_tag .php%{php_major_version}}

%define real_name php-pecl-apc
%define base_ver 3.0
%define php_base php52

Summary:       APC caches and optimizes PHP intermediate code
Name:          %{php_base}-pecl-apc
Version:       3.1.9
Release:       2.ius%{?dist}
License:       PHP
Group:         Development/Languages
Vendor:        Rackspace US, Inc.
URL:           http://pecl.php.net/package/APC
Source:        http://pecl.php.net/get/APC-%{version}.tgz
Source1:       apc.ini

# PECL Bug #20529 
# http://pecl.php.net/bugs/bug.php?id=20529
#Patch1:	       pecl_bug_20529-relative-files-not-cached.patch

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
Conflicts:     %{php_base}-mmcache %{php_base}-eaccelerator 
Conflicts:     %{php_base}-zend-optimizer %{php_base}zend-optimizer
Provides:      %{real_name} = %{version}
Conflicts:     %{real_name} < %{base_ver}
BuildRequires: %{php_base}-devel %{php_base} %{php_base}-cli
BuildRequires: httpd-devel %{php_base}-pear 
%if %{?php_zend_api}0
# Require clean ABI/API versions if available (Fedora)
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}
%else
%if "%{rhel}" == "5"
# RHEL5 where we have php-common providing the Zend ABI the "old way"
Requires:      %{php_base}-zend-abi = %{php_zendabiver}
%else
# RHEL4 where we have no php-common and nothing providing the Zend ABI...
Requires:      %{php_base} = %{php_version}
%endif
%endif
Provides:      php-pecl(%{pecl_name}) = %{version}-%{release}
Provides:      %{php_base}-pecl(%{pecl_name}) = %{version}-%{release}

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

%description
APC is a free, open, and robust framework for caching and optimizing PHP
intermediate code.

%prep
%setup -q -n %{pecl_name}-%{version}

%build
%{_bindir}/phpize
%configure --enable-apc-memprotect --with-apxs=%{_sbindir}/apxs --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Install the package XML file
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 ../package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__install} -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/php.d/apc.ini

# Fix the charset of NOTICE
iconv -f iso-8859-1 -t utf8 NOTICE >NOTICE.utf8
mv NOTICE.utf8 NOTICE

%post
%{__pecl} install --nodeps --soft --force --register-only --nobuild %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]  ; then
%{__pecl} uninstall --nodeps --ignore-errors --register-only %{pecl_name} >/dev/null || :
fi

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc TECHNOTES.txt CHANGELOG LICENSE NOTICE TODO INSTALL apc.php
%config(noreplace) %{_sysconfdir}/php.d/apc.ini
%{php_extdir}/apc.so
%{pecl_xmldir}/%{pecl_name}.xml
%{_includedir}/php/ext/apc/apc_serializer.h

%changelog
* Wed May 25 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-2.ius
- Majority of apc.ini is commented out to allow APC's defaults
  to take control
- apc.ini is now installed from %%{SOURCE1} rather standardout

* Mon May 16 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.9

* Wed May 04 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.8-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.8

* Tue Apr 26 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.7-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.7
- Removed Patch1 pecl_bug_20529-relative-files-not-cached.patch
  software is not compiling with patch in place, need to test against
  bug http://www.pecl.php.net/bugs/bug.php?id=20529&edit=1

* Wed Feb 23 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.6-3.ius
- Adding: Patch1: pecl_bug_20529-relative-files-not-cached.patch

* Tue Dec 28 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.6-2.ius
- Option '--enable-apc-mmap' became '--enable-apc-memprotect'.
- Add the 'M' suffix on memory values in the .ini settings per new
  config rules.

* Thu Dec 16 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.6-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.6
- Rebuild against php52-5.2.16
- BuildRequires: php52-cli

* Mon Jul 27 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.0.19-5.ius
- Rebuild for php 5.2.14

* Thu Dec 17 2009 BJ Dierkes <wdierkes@rackspace.com> - 0:3.0.19-4.ius
- Rebuild against latest php52-5.2.12 sources
- BuildRequires: php52-pear

* Fri Oct 16 2009 BJ Dierkes <wdierkes@rackspace.com> - 0:3.0.19-3.ius
- Rebuilding for IUS

* Mon Sep 28 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:3.0.19-2.1.rs
- Rebuilding against new php.

* Mon Sep 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:3.0.19-2.rs
- Adding Epoch: 1 due to conflicts with EPEL packages and stock php.

* Fri Jan 23 2009 BJ Dierkes <wdierkes@rackspace.com> - 3.0.19-1.2.rs
- Adding php_ver_tag to release for different major versions of PHP.
- Conflicts with php-zend-optimizer

* Tue Jan 06 2009 BJ Dierkes <wdierkes@rackspace.com> - 3.0.19-1.1.rs
- Rebuild

* Wed Jun 25 2008 Tim Jackson <rpm@timj.co.uk> - 3.0.19-1
- Update to 3.0.19
- Fix PHP Zend API/ABI dependencies to work on EL-4/5
- Fix "License" tag
- Fix encoding of "NOTICE" file
- Add registration via PECL

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.0.14-3
- Autorebuild for GCC 4.3

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 3.0.14-2
- Rebuild for selinux ppc32 issue.

* Thu Jun 28 2007 Chris Chabot <chabotc@xs4all.nl> - 3.0.14-1
- Updated to 3.0.14
- Included new php api snipplets

* Fri Sep 15 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.12-5
- Updated to new upstream version

* Mon Sep 11 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-5
- FC6 rebuild 

* Sun Aug 13 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-4
- FC6T2 rebuild

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-3
- Renamed to php-pecl-apc and added provides php-apc
- Removed php version string from the package version

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-2
- Trimmed down BuildRequires
- Added Provices php-pecl(apc)

* Sun Jun 18 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-1
- Initial package, templated on already existing php-json 
  and php-eaccelerator packages
