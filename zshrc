export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
HYPHEN_INSENSITIVE="true"

zstyle ':omz:update' mode auto      # update automatically without asking
zstyle ':omz:update' frequency 10

alias rsync='rsync --stats --cc=xxh3 --compress --zc=zstd -P'

plugins=(gitfast git rsync fzf history aws)

# ZSH settings
setopt BANG_HIST
setopt EXTENDED_HISTORY
#setopt HIST_EXPIRE_DUPS_FIRST

source $ZSH/oh-my-zsh.sh

# Make zsh know about hosts already accessed by SSH
zstyle -e ':completion:*:(ssh|scp|sftp|rsh|rsync):hosts' hosts 'reply=(${=${${(f)"$(cat {/etc/ssh_,~/.ssh/known_}hosts(|2)(N) /dev/null)"}%%[# ]*}//,/ })'

export PATH="$HOME/go/bin:$HOME/.local/bin/:$PATH"

# editor for file types
alias -s zsh=vim
alias -s h=vim
alias -s cpp=vim
alias -s jnlp='javaws -Xnosplash'

# ==================================================================

# command alias
alias t='tail -f'
#alias h='history'
alias hgrep="fc -El 0 | grep"
alias time='/usr/bin/time -v'


# apt
alias agi='apt install'
alias aguu='apt update && apt upgrade'
alias acs='apt search'

alias pstree='pstree -lnpa'

# maven
#alias mvn=mvn-color
export MAVEN_OPTS='-Dmaven.artifact.threads=32'

# less
export LESS='--ignore-case --RAW-CONTROL-CHARS --HILITE-UNREAD --LONG-PROMPT --tabs=4 --window=-4'
#export LESS_TERMCAP_mb=$'\E[1;31m'
#export LESS_TERMCAP_md=$'\E[1;36m'
#export LESS_TERMCAP_me=$'\E[0m'
#export LESS_TERMCAP_so=$'\E[01;44;33m'
#export LESS_TERMCAP_se=$'\E[0m'
#export LESS_TERMCAP_us=$'\E[1;32m'
#export LESS_TERMCAP_ue=$'\E[0m'

# golang
export GOPATH="$HOME/go"
export GOBIN="$GOPATH/bin"
export GOOS=linux GOARCH=amd64 GOAMD64=v4 CGO_ENABLED=0

export EDITOR='vim'

# batcat
export BAT_THEME='Monokai Extended Bright'
export BAT_STYLE='header,numbers,grid'

# manpage
#export MANPAGER="sh -c 'col -bx | batcat -l man -p'"
# export MANROFFOPT="-c"

alias ug='ug --heading --smart-case --line-number --dereference-recursive'

export ANDROID_HOME=/usr/lib/android-sdk
export ANDROID_NDK_HOME=/usr/lib/android-ndk

[ -f $HOME/.custom.zsh ] && source $HOME/.custom.zsh
