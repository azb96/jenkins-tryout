%define name        cpaas-batch-service
%define release     %{_new_rpm_release}
%define version     %{_new_rpm_version}
%define buildroot   %{_topdir}/%{name}-%{version}-root
%define _prefix     /var/mcp/packages
%define _gitbranch  %{_new_gitbranch}
%define docker_image_version %{_new_docker_image_version}

BuildRoot:     %{buildroot}
Summary:       Builds and installs %{name}-%{version}-%{release} locally
Name:          %{name}
Version:       %{version}
Release:       %{release}
Group:         Platform
License:       N/A
URL:           ssh://git@bitbucket.genband.com:7999/nuv/cpaas_batch_service.git
Vendor:        Genband
Source:        %{name}-%{version}-%{release}.tar.gz
Prefix:        %{_prefix}
Packager:      genband
Requires:      api-gw minio

%description
%{name}-%{version}-%{release}.rpm unpackages a pre-built Docker image for the %{name} service and pushes it to a Docker registry.
Then, it unpackages an Ansible script, which creates and starts %{name}.

%prep
# Cleanout build subdirs
rm -Rf %{_topdir}/BUILD/*
rm -Rf %{_topdir}/BUILDROOT/*
rm -Rf %{_topdir}/SRPMS/*
rm -Rf %{_topdir}/RPMS/*
rm -Rf %{_topdir}/SOURCES/*

# Checkout source from BitBucket
rsync -r %{_topdir}/..// %{_topdir}/SOURCES/%{name}
cd %{_topdir}/SOURCES/%{name}

# Change to specified branch of code
#if [ ! `git checkout %{_gitbranch}` ]; then git checkout master; fi

# In order for the packager to access the correct Docker image(s), it must retrieve the version number(s) from the config.yml file.
# Retrieve path to config.yml
config_path=$(find . -print | grep -i '/config.yml')

# Store <name>-config.yml variables in shell
while read config_file_line
do
  if [[ ${config_file_line} != "#"* ]] && [[ ${config_file_line} != "" ]]
  then
    parse1=$(echo ${config_file_line} | cut -f1 -d":")
    parse2=$(echo '=$(echo "')
    parse3=$(echo ${config_file_line} | sed 's/.*: //1')
    parse4=$(echo '")')
    eval ${parse1}${parse2}${parse3}${parse4}
  fi
done < ${config_path}

# Make ansible directories
mkdir -p %{_topdir}/SOURCES/ansible_guest/roles

# Retrieve path to deployment directory
deployment_path=$(find -name deployment -type d -print | grep -v '.git/' | head -n1)

# Copy source files into ansible directories
cp %{_topdir}/SOURCES/%{name}/${deployment_path}/ansible/ansible_%{name}.yml %{_topdir}/SOURCES/ansible_guest/ansible_%{name}-%{version}-%{release}.yml
cp %{_topdir}/SOURCES/%{name}/${deployment_path}/ansible/ansible_portal-db.yml %{_topdir}/SOURCES/ansible_guest/ansible_portal-db-%{name}-%{version}-%{release}.yml
cp -r %{_topdir}/SOURCES/%{name}/${deployment_path}/ansible/setup-%{name} %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}

# Make directories for files and templates
mkdir -p %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/docker
mkdir -p %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/templates

mkdir -p %{_topdir}/SOURCES/ansible_guest/roles/security/manage-database-secret/files

# Copy <name>-config.yml into the files directory
cp ${config_path} %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/config-%{name}-%{version}-%{release}.yml
echo "version: '%{version}'" >> %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/config-%{name}-%{version}-%{release}.yml
echo "release: '%{release}'" >> %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/config-%{name}-%{version}-%{release}.yml
echo "image_version: '%{docker_image_version}'" >> %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/config-%{name}-%{version}-%{release}.yml

cp %{_topdir}/SOURCES/%{name}/${deployment_path}/ansible/portal-db-config.yml %{_topdir}/SOURCES/ansible_guest/roles/security/manage-database-secret/files/portal-db-config-%{name}-%{version}-%{release}.yml

# Update contents of ansible_%{name}-%{version}-%{release}.yml to reflect versioning
sed -i "s/config.yml/config-%{name}-%{version}-%{release}.yml/g" %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/tasks/main.yml
sed -i "s/config.yml/config-%{name}-%{version}-%{release}.yml/g" %{_topdir}/SOURCES/ansible_guest/ansible_portal-db-%{name}-%{version}-%{release}.yml
sed -i "s/config.yml/config-%{name}-%{version}-%{release}.yml/g" %{_topdir}/SOURCES/ansible_guest/ansible_%{name}-%{version}-%{release}.yml

# Copy deployment directories into templates folder for text decoration
# Retrieve all directory names except ansible
directory_names=($(ls -I "ansible" -I "makefile" -I "docker" ${deployment_path}))

# Loop through every directory except ansible
for i in "${directory_names[@]}"
do
  # Read file names from the directory
  cd %{_topdir}/SOURCES/%{name}/${deployment_path}/${i}
  file_names=($(ls))

  # Make directories for service
  mkdir -p %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/templates/${i}

  # Copy files to the source code
  for j in "${file_names[@]}"
  do
    filename=$(echo ${j} | cut -f1 -d".")
    extension=$(echo ${j} | cut -f2 -d".")
    cp %{_topdir}/SOURCES/%{name}/${deployment_path}/${i}/${j} %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/templates/${i}/${filename}-%{version}-%{release}.${extension}.j2
  done
done

cd %{_topdir}/SOURCES/%{name}
if [ -d "${deployment_path}/nginx" ]
then
  cp -r ${deployment_path}/nginx %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/
fi

# Checkout source images from Docker repo
docker save ${docker_fqdn}/${image_name}:%{docker_image_version} > %{_topdir}/SOURCES/ansible_guest/roles/setup-%{name}/files/docker/${image_tar}

# Create a tarball from the source files
cd %{_topdir}/SOURCES
tar -chvzf %{name}-%{version}-%{release}.tar.gz ansible_guest/* 

# Run a modified %setup macro to unpack the source files
cd %{_topdir}/BUILD/
rm -rf %{_topdir}/BUILD/ansible_guest
/usr/bin/gzip -dc %{_topdir}/SOURCES/%{name}-%{version}-%{release}.tar.gz | /usr/bin/tar -xvvf -
cd %{_topdir}/BUILD/ansible_guest
/usr/bin/chmod -Rf a+rX,u+w,g-w,o-w .

%install
# Create a directory to where the package will be installed, then copy the package contents to it.
rm -rf $RPM_BUILD_ROOT
mkdir -p "$RPM_BUILD_ROOT%{_prefix}/%{name}-%{version}-%{release}"
cp -R * "$RPM_BUILD_ROOT%{_prefix}/%{name}-%{version}-%{release}"

%files
%defattr(-,root,root)
%{_prefix}/%{name}-%{version}-%{release}

%pre
%include %{_buildscripts}/pre-install-sudo.sh
%include %{_buildscripts}/pre-install-vault.sh

if [ $1 == 2 ]; then
  # Check /var/mcp/packages to see what's currently installed
  prev_version=$(ls %{_prefix} | grep -m 1 %{name} | cut -f2 -d'-')
  prev_release=$(ls %{_prefix} | grep -m 1 %{name} | cut -f3 -d'-')

  # Create a temporary file with the previous package name and version
  echo "prev_version: $prev_version" > /tmp/prev-%{name}
  echo "prev_release: $prev_release" >> /tmp/prev-%{name}
fi

%post -p /bin/sh
ansible_sudo=$(</etc/ansible_guest/group_vars/ansible_sudo)

# If there is an existing service by the same name, run its uninstall script
if [ $1 == 2 ]; then
  # Read the temporary file to identify which package to uninstall
  prev_version=$(grep -ir "version" /tmp/prev-%{name} | cut -f2 -d" ")
  prev_release=$(grep -ir "release" /tmp/prev-%{name} | cut -f2 -d" ")
  old_playbook=$(ls /etc/ansible_guest/ | grep "ansible_%{name}-${prev_version}-${prev_release}" | grep -v "retry")

  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/${old_playbook} -i /etc/ansible_guest/hosts -vv --tags "uninstall" -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file /etc/ansible_guest/group_vars/vault | tee -a /var/log/ansible.log
fi

cp -R %{_prefix}/%{name}-%{version}-%{release}/ansible_guest/* /etc/ansible_guest/
/bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/ansible_%{name}-%{version}-%{release}.yml -i /etc/ansible_guest/hosts -vv --tags "stage" -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file /etc/ansible_guest/group_vars/vault | tee -a /var/log/ansible.log

# Check if the service is already installed.
# If not, install from scratch.
# If so, upgrade (or rollback) the service.
service_check=$(kubectl get svc --all-namespaces | grep -w %{name} | xargs | cut -f2 -d" ")
if [ -z "${service_check}" ]
then
  kubectl create namespace portal
  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/ansible_portal-db-%{name}-%{version}-%{release}.yml -i /etc/ansible_guest/hosts -vv -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file=/etc/ansible_guest/group_vars/vault 2>&1 | tee -a /var/log/ansible.log
  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/patch/AEB-3428-add-minio-vip.yml -i /etc/ansible_guest/hosts -vv -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file=/etc/ansible_guest/group_vars/vault 2>&1 | tee -a /var/log/ansible.log
  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/minio.yml -i /etc/ansible_guest/hosts -vv -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file=/etc/ansible_guest/group_vars/vault 2>&1 | tee -a /var/log/ansible.log
  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/ansible_%{name}-%{version}-%{release}.yml -i /etc/ansible_guest/hosts -vv --tags "install" -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file /etc/ansible_guest/group_vars/vault | tee -a /var/log/ansible.log
else
  if [ $AUTO_APPLY_UPGRADE == 0 ]
  then
    :
  else
    /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/ansible_%{name}-%{version}-%{release}.yml -i /etc/ansible_guest/hosts -vv --tags "upgrade" -e "ansible_sudo_pass=${ansible_sudo}" --vault-password-file /etc/ansible_guest/group_vars/vault | tee -a /var/log/ansible.log
  fi
fi

%preun -p /bin/sh
if [ $1 == 0 ]; then
  %include %{_buildscripts}/pre-install-sudo.sh
  %include %{_buildscripts}/preun-temp-file.sh
fi

%postun -p /bin/sh
%include %{_buildscripts}/postun-teardown-service.sh

if [ $1 == 0 ]; then
  ansible_sudo=$(</etc/ansible_guest/group_vars/ansible_sudo)

  # Run the uninstall script
  uninstall_playbook=$(ls /etc/ansible_guest/ | grep "ansible_%{name}-%{version}-%{release}" | grep -v "retry")
  /bin/sudo -u sysadm ansible-playbook /etc/ansible_guest/${uninstall_playbook} -i /etc/ansible_guest/hosts -vv --tags "uninstall" -e "ansible_sudo_pass=${ansible_sudo}" | tee -a /var/log/ansible.log
fi

%changelog
* Tue Aug 01 2017 Alex Bloor <alexander.bloor@kandy.io> 1.0.08-01
- Updated with template for spec file
* Thu Jul 20 2017 Alex Bloor <alexander.bloor@kandy.io> 1.0.7-20
- Separated docker registry fqdn from image names
* Mon Jun 05 2017 Alex Bloor <alexander.bloor@kandy.io> 1.0.6-5
- Initial build
