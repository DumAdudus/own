#plugins=(command-not-found thefuck history-substring-search history zsh-navigation-tools zsh-completions)
#plugins+=(git dircycle jsontools mvn zsh_reload zsh-256color themes)
#plugins+=(zsh-syntax-highlighting zsh-autosuggestions)

# ZSH settings
setopt BANG_HIST
setopt EXTENDED_HISTORY
#setopt HIST_EXPIRE_DUPS_FIRST

alias -s zsh=vim
alias -s h=vim
alias -s cpp=vim
alias -s jnlp='javaws -Xnosplash'

alias t='tail -f'
#alias h='history'
alias hgrep="fc -El 0 | grep"
alias time='/usr/bin/time -v'

# Make zsh know about hosts already accessed by SSH
zstyle -e ':completion:*:(ssh|scp|sftp|rsh|rsync):hosts' hosts 'reply=(${=${${(f)"$(cat {/etc/ssh_,~/.ssh/known_}hosts(|2)(N) /dev/null)"}%%[# ]*}//,/ })'

# ==================================================================
# apt
alias agi='apt install'
alias aguu='apt update && apt upgrade'
alias acs='apt search'

alias pstree='pstree -lnpa'
alias rsync='rsync -uazhP'

# maven
alias mvn=mvn-color
alias rebld='mvn clean package -Dmaven.test.skip=true'
alias mvncv='mvn clean clover2:setup test clover2:aggregate clover2:clover'
export MAVEN_OPTS='-Dmaven.artifact.threads=32'
mvnsocks () {
    export MAVEN_OPTS="$MAVEN_OPTS -DsocksProxyHost=10.200.211.254 -DsocksProxyPort=1080"
}

# SCM
#export CVSROOT=:ext:brianma@rmncvs.rmnus.sen.symantec.com:/nbe/CVS
#export P4CONFIG=.p4config
export P4PORT=ssl:perforce.community.veritas.com:9666
export P4USER=brian.ma
export P4CLIENT=nbapp_bma

# My binaries
export PATH=$PATH:/home/dumas/usr/local/bin:/home/dumas/.cargo/bin/

# cruadv
export CAP_PYOUT=1
