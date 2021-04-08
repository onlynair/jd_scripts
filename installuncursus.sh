#!/bin/bash
if [ "$EUID" -ne 0 ]; then
echo You need to run this script as root.
else
need=""
command -v unzip >/dev/null 2>&1 || need+="unzip "
command -v plutil >/dev/null 2>&1 || need+="com.bingner.plutil "
command -v curl >/dev/null 2>&1 || need+="curl "
command -v wget >/dev/null 2>&1 || need+="wget "
clear
echo -e "\e[31mWelcome to Uncursus Installation Script V2.0.2 (Stable) By @Yaya4_4 on Twitter.\e[0m"
echo "Checking if this script is running on ARM Darwin"
if [ $(uname) = "Linux" ]; then
	if [ $(uname -p) = "x86_64" ]; then
		PC=yes
  fi
fi
if [[ "${PC}" = yes ]]; then
echo "Use this script with SSH over an IP session on your iDevice. Thanks."
exit  1
     else
    echo "ARM Darwin detected, running..."
echo "Checking if you're using a clean install of unc0ver..."
if [[ -f "/.installed_unc0ver" ]]; then
              u0=yes
                  else
                     u0=no
                   fi
if [[ "${u0}" = no ]]; then
echo "Use unc0ver, thanks"
exit  1
else 
echo "unc0ver detected"
echo "WARNING: I'M NOT RESPONSIBLE IF ANYTHING GOES WRONG"
echo "If you've found any bugs, please create an issue in GitHub."
echo "Checking Dependencies..."
if [[ $need != "" ]]; then
echo "Installing Dependencies..."
apt update
apt install $need -y
fi

echo "Pulling and executing the Procursus Migration Script"
/bin/bash -c "$(curl -fsSL https://file.wzwweb.ml/uncursus/procursus-migration.sh)"
VER=$(/usr/bin/plutil -key ProductVersion /System/Library/CoreServices/SystemVersion.plist)
if [[ "${VER%.*}" -ge 12 ]] && [[ "${VER%.*}" -lt 13 ]]; then
	CFVER="chimera"
elif [[ "${VER%.*}" -ge 13 ]] && [[ "${VER%.*}" -lt 14 ]]; then
	CFVER="odyssey"
elif [[ "${VER%.*}" -ge 14 ]]; then
	CFVER="taurine"
else
	if [[ "${VER%.*.*}" -ge 14 ]]; then
		CFVER="taurine"
	else
		if [[ "${VER%.*.*}" -ge 13 ]]; then
			CFVER="odyssey"
		else
			if [[ "${VER%.*.*}" -ge 12 ]]; then
				CFVER="chimera"
			fi
		fi
	fi
fi
echo "Creating a custom directory for the required files. Path (/User/Documents/uncursus)."
rm -rf /User/Documents/uncursus
mkdir /User/Documents/uncursus
mkdir /User/Documents/uncursus/u0
echo "Done. Setuping Uncursus Repo...."
echo "Types: deb" > /etc/apt/sources.list.d/uncursus.sources
echo "URIs: https://repo.wzwweb.ml/uncursus/" >> /etc/apt/sources.list.d/uncursus.sources
echo "Suites: ./" >> /etc/apt/sources.list.d/uncursus.sources
echo "Components: " >> /etc/apt/sources.list.d/uncursus.sources
echo "" >> /etc/apt/sources.list.d/uncursus.sources
mkdir -p /etc/apt/preferences.d/

echo "Package: *" > /etc/apt/preferences.d/cydia
echo "Pin: release n=uncursus-ios" >> /etc/apt/preferences.d/cydia
echo "Pin-Priority: 1001" >> /etc/apt/preferences.d/cydia
echo "" >> /etc/apt/preferences.d/cydia
echo "Package: *" >> /etc/apt/preferences.d/cydia
echo "Pin: release o=Procursus" >> /etc/apt/preferences.d/cydia
echo "Pin-Priority: 501" >> /etc/apt/preferences.d/cydia
echo "" >> /etc/apt/preferences.d/cydia
echo "Package: *" >> /etc/apt/preferences.d/cydia
echo "Pin: release o=Bingner/Elucubratus" >> /etc/apt/preferences.d/cydia
echo "Pin-Priority: 10" >> /etc/apt/preferences.d/cydia
echo "" >> /etc/apt/preferences.d/cydia

echo "Done. Installing Sileo"
apt update
apt install org.coolstar.sileo -y
uicache -p /Applications/Sileo.app
apt autoremove -y

echo "Done. Downloading necessities"
wget -q https://file.wzwweb.ml/uncursus/DebPatch.zip --directory-prefix=/User/Documents/uncursus/
unzip /User/Documents/uncursus/DebPatch.zip -d /User/Documents/uncursus/debpatch
rm -rf /usr/bin/cynject
wget -q https://repo.wzwweb.ml/uncursus/debs/com.ex.substitute_2.0.9_iphoneos-arm.deb --directory-prefix=/User/Documents/uncursus/u0
wget -q https://repo.wzwweb.ml/uncursus/debs/com.saurik.substrate.safemode_0.9.6005_iphoneos-arm.deb --directory-prefix=/User/Documents/uncursus/u0
echo "Done. Installing necessities..."
dpkg -i --force-all /User/Documents/uncursus/debpatch/libssl1.1.deb
dpkg -i --force-all /User/Documents/uncursus/debpatch/*.deb
dpkg -i --force-all /User/Documents/uncursus/u0/*.deb
echo "Done. Running Firmware Configuration (./firmware.sh)"
/usr/libexec/firmware
echo "Bootstrap installation complete. Cleaning up..."
rm -rf /User/Documents/uncursus/
echo "Uninstalling Cydia..."
apt purge cydia -y
rm -rf /private/var/mobile/Library/Caches/com.saurik.Cydia
rm -rf /private/var/mobile/Library/Cydia
rm -f /private/var/mobile/Library/Preferences/com.saurik.Cydia.plist
killall -9 cfprefsd
uicache -a
echo "All Done."
apt purge berkeleydb nettle org.thebigboss.repo.icons -y
apt autoremove -y
touch /.installed_${CFVER}
touch /.procursus_strapped
sbreload
fi
fi
fi
